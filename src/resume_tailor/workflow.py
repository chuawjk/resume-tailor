"""LlamaIndex workflow for the resume-tailoring pipeline."""

import logging

from llama_index.core.workflow import (
    Context,
    HumanResponseEvent,
    InputRequiredEvent,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from resume_tailor.agents.cv_extraction.agent import extract_cv
from resume_tailor.agents.fabrication_judge.agent import judge_fabrication
from resume_tailor.agents.gap_analysis.agent import analyse_gaps
from resume_tailor.agents.jd_extraction.agent import extract_jd
from resume_tailor.agents.resume_tailoring.agent import tailor_resume

logger = logging.getLogger(__name__)


class ResumeStartEvent(StartEvent):
    cv_text: str
    jd_text: str


class Checkpoint1RequestEvent(InputRequiredEvent):
    jd_profile: dict
    cv_profile: dict


class Checkpoint1ResponseEvent(HumanResponseEvent):
    jd_profile: dict
    cv_profile: dict


class Checkpoint2RequestEvent(InputRequiredEvent):
    gap_analysis: dict


class Checkpoint2ResponseEvent(HumanResponseEvent):
    gap_analysis: dict


class Checkpoint3RequestEvent(InputRequiredEvent):
    tailored_resume: str
    fabrication_report: dict


class Checkpoint3ResponseEvent(HumanResponseEvent):
    final_resume: str


class ResumeWorkflow(Workflow):
    @step
    async def extract(self, ctx: Context, ev: ResumeStartEvent) -> Checkpoint1RequestEvent:
        logger.info("Pipeline stage: entering extraction")
        jd_profile = extract_jd(ev.jd_text)
        cv_profile = extract_cv(ev.cv_text)
        await ctx.store.set("cv_profile", cv_profile)
        await ctx.store.set("jd_profile", jd_profile)
        logger.info("Pipeline stage: extraction complete")
        return Checkpoint1RequestEvent(jd_profile=jd_profile, cv_profile=cv_profile)

    @step
    async def gap_analysis(
        self, _ctx: Context, ev: Checkpoint1ResponseEvent
    ) -> Checkpoint2RequestEvent:
        logger.info("Pipeline stage: entering gap analysis")
        gap = analyse_gaps(ev.jd_profile, ev.cv_profile)
        logger.info("Pipeline stage: gap analysis complete")
        return Checkpoint2RequestEvent(gap_analysis=gap)

    @step
    async def tailor_and_judge(
        self, ctx: Context, ev: Checkpoint2ResponseEvent
    ) -> Checkpoint3RequestEvent:
        logger.info("Pipeline stage: entering tailoring")
        cv_profile = await ctx.store.get("cv_profile")
        jd_profile = await ctx.store.get("jd_profile")
        tailored = tailor_resume(cv_profile, jd_profile, ev.gap_analysis)
        report = judge_fabrication(tailored, cv_profile)
        logger.info("Pipeline stage: tailoring and fabrication check complete")
        return Checkpoint3RequestEvent(tailored_resume=tailored, fabrication_report=report)

    @step
    async def finalise(self, _ctx: Context, ev: Checkpoint3ResponseEvent) -> StopEvent:
        logger.info("Pipeline stage: finalising")
        return StopEvent(result=ev.final_resume)
