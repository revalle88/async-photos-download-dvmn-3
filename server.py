import aiofiles
import asyncio
import logging
import os
from aiohttp import web

import settings

logger = logging.getLogger(__name__)


class ArchiveHandler:
    def __init__(self, archive_path):
        self.proc = None
        self.archive_path = archive_path

    async def start_archive_process(self):
        self.proc = await asyncio.create_subprocess_exec(
            "zip",
            "-r",
            "-",
            f".",
            "*",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.archive_path,
        )

    async def stop_archive_process(self):
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            await self.proc.communicate()


async def archive(request):
    archive_hash = request.match_info.get("archive_hash", None)
    cwd = os.getcwd()
    archive_path = (
        f"{cwd}/test_photos/{archive_hash}/"
        if not settings.photos_directory
        else f"{settings.photos_directory}/test_photos/{archive_hash}/"
    )
    if not os.path.exists(archive_path):
        raise web.HTTPNotFound()
    response = web.StreamResponse()
    response.headers["Content-Type"] = "application/octet-stream"
    response.headers["Content-Disposition"] = "attachment; filename=photos.zip"
    await response.prepare(request)

    archive_handler = ArchiveHandler(archive_path=archive_path)
    await archive_handler.start_archive_process()

    chunk_number = 0
    try:
        while not archive_handler.proc.stdout.at_eof():
            logger.info(f"Sending archive chunk {chunk_number}")
            if settings.response_delay:
                await asyncio.sleep(settings.response_delay)
            await response.write(
                await archive_handler.proc.stdout.read(n=settings.CHUNK_SIZE)
            )
            chunk_number += 1
    except ConnectionResetError:
        logger.error(f"Download was interrupted, terminating zip process")
    except Exception:
        logger.error(f"Exception, terminating zip process")
    finally:
        await archive_handler.stop_archive_process()
        return response


async def handle_index_page(request):
    async with aiofiles.open("index.html", mode="r") as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type="text/html")


async def main():
    settings.init_config()
    if settings.logging_enabled:
        logging.basicConfig(level=logging.DEBUG)
    app = web.Application()
    app.add_routes(
        [
            web.get("/", handle_index_page),
            web.get("/archive/{archive_hash}/", archive),
        ]
    )
    web.run_app(app)


if __name__ == "__main__":
    await main()
