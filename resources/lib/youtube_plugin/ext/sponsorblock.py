import traceback

import requests

from ..kodion import logger

BASE_URL = "https://api.sponsor.ajay.app/api"

GET_VIDEO_SPONSOR_TIMES = BASE_URL + "/getVideoSponsorTimes"

STR_SKIPPED_SPONSOR = 30733


def _parse_cutlist(raw_cutlist):
    cutlist = []
    for start, end in raw_cutlist:
        if start >= end:
            raise ValueError("start must be smaller than end")

        cutlist.append({
            "start": start,
            "end": end,
            "notification": STR_SKIPPED_SPONSOR
        })

    return cutlist


def get_sponsor_cutlist(video_id):  # type: (str) -> Optional[List[dict]]
    logger.log_debug("[SponsorBlock] getting sponsor times for %s" % video_id)
    with requests.get(GET_VIDEO_SPONSOR_TIMES, params={"videoID": video_id}) as resp:
        try:
            data = resp.json()
        except ValueError:
            if resp.status_code == 404:
                logger.log_debug("[SponsorBlock] no reported sponsor segments")
            else:
                logger.log_error("[SponserBlock] invalid response:\n%s" % traceback.format_exc())

            return None

    try:
        return _parse_cutlist(data["sponsorTimes"])
    except Exception:
        logger.log_error("[SponserBlock] unable to parse sponsor times:\n%s" % traceback.format_exc())
        return None
