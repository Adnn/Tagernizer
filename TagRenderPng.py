#!/usr/bin/env python3
import argparse, asyncio, os
import urllib.parse

from playwright.async_api import async_playwright


def is_url(url):
    """ Return boolean indicating url validity """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


async def render_list(destination_folder, *ids):
    """ The snake people call that a coroutine afaik """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page()
            for occurrence_id in ids:
                tag_url = urllib.parse.urljoin(
                    args.origin,
                    "media/advideogame/occurrences/{}/tags/v2.html".format(occurrence_id))
                if not is_url(tag_url):
                    print("Error: invalid url '{}'".format(tag_url))
                    break
                options = {
                    "path": os.path.join(destination_folder, "tag_{}.png".format(occurrence_id)),
                    "full_page": True
                }
                response = await page.goto(tag_url)
                if response.ok:
                    await page.screenshot(**options)
        except Exception as e:
            print("Exception: {}".format(e))
        await browser.close()


async def main(args):
    """ Asynchronous entrypoint """
    first_id = args.occurrence_id
    last_id = args.until if args.until else first_id
    #await asyncio.gather(*[render(args.destination, id) for id in range(first_id, last_id+1)])
    await render_list(args.destination, *range(first_id, last_id+1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Render HTML tags as PNG images.")
    parser.add_argument('origin',
                        help="The origin serving Collecster (e.g. https://www.collecster.com)")
    parser.add_argument('destination',
                        help="The directory receiving rendered images")
    parser.add_argument("occurrence_id", type=int,
                        help="first occurrence to render, only one unless --until is specified")
    parser.add_argument("--until", type=int,
                        help="render interval from occurrence_id until this optional id inclusive")

    args = parser.parse_args()

    if not os.path.exists(args.destination):
        os.makedirs(args.destination)

    ## Simpler run is not used, because it sporadically errors on exit
    ##      RuntimeError: Event loop is closed
    #asyncio.run(main(args))
    ## This is deprecated since Python 3.11, there is no current event loop
    #asyncio.get_event_loop().run_until_complete(main(args))

    # see: https://stackoverflow.com/a/73367187
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(args))
