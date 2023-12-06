import os
import requests
from http import HTTPStatus

from og import extract_opengraph_from_html


USER_AGENT = os.environ.get("OG_USER_AGENT", "TelegramBot (like TwitterBot)")


def main(args):
      url = args.get("url", "")

      if not url.startswith("http"):
            return { "statusCode": HTTPStatus.BAD_REQUEST }

      res = requests.get(url, headers={ "User-Agent": USER_AGENT })
      
      if res.status_code != 200:
            return { "statusCode": HTTPStatus.BAD_REQUEST, "body": f"{res.status_code}" }
      
      return {
            "headers": { 
                  "Content-Type": "application/json" 
            },
            "body": extract_opengraph_from_html(res.content)
      }
