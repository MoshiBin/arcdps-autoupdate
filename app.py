import os.path
import requests
import hashlib
import tomllib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s"
)
with open("config.toml", "rb") as f:
    conf = tomllib.load(f)
arcdps_full_path = os.path.join(conf["gw2_folder"], conf["arcdps_filename"])

ses = requests.Session()
ses.headers.update({"User-Agent": "ArcDPS AutoUpdate v0"})


def get_our_arcdps_hash():
    if not os.path.exists(arcdps_full_path):
        logging.warning("arcdps not found, installing for the first time")
        return None
    with open(arcdps_full_path, "rb") as arcdps_file:
        return hashlib.file_digest(arcdps_file, "md5").hexdigest()


def get_remote_arcdps_hash():
    resp = ses.get(f"{conf['advanced']['arcdps_url']}d3d11.dll.md5sum")
    return resp.text.strip().split()[0]


def read_config_file(location="config.toml"):
    with open(location, "rb") as f:
        data = tomllib.load(f)
    return data


def download_arcdps():
    resp = ses.get(f"{conf['advanced']['arcdps_url']}d3d11.dll", stream=True)
    with open(arcdps_full_path, "wb") as arcdps_file:
        for chunk in resp.iter_content(chunk_size=128):
            arcdps_file.write(chunk)


def main():
    remote_hash = get_remote_arcdps_hash()
    our_hash = get_our_arcdps_hash()
    if remote_hash == our_hash:
        logging.info("We are up to date, not replacing existing arcdps")
        return
    logging.info(f"ArcDPS outdated (ours={our_hash}, theirs={remote_hash}), updating")
    download_arcdps()
    logging.info("Finished downloading, checking hash again")
    our_hash = get_our_arcdps_hash()
    if remote_hash == our_hash:
        logging.info(f"Done! (ours={our_hash}, theirs={remote_hash}")
    else:
        logging.fatal(f"New hash does not match! ({our_hash} != {remote_hash}")


if __name__ == "__main__":
    main()
    input("Press the <Enter> key on the keyboard to exit.")