# lists all the videos that are available
import os
import json
import shutil


def upload_video(base_path,videoname):
    """copies the uploaded video from the uploads folder into the static/videos folder"""
    videos_full_path = os.path.join(base_path,"uploads",videoname)
    print(videos_full_path)
    dest = os.path.join(base_path,"static","videos")
    print(dest)
    shutil.move(src=videos_full_path,dst=dest)


def get_link_list(base_path):
    """gets all the links you have already added to the reader"""
    with open(os.path.join(base_path,"static","videos", "video_links.json"),"r") as video_links:
        videolinks = json.load(video_links)

    return videolinks

def get_video_list(base_path) -> list:
    """get all the video files, youtube or server side"""
    files = os.listdir(os.path.join(base_path,"static","videos"))
    all_videos = []
    for file in files:
        if ".json" in file:
            continue
        else:
            all_videos.append("./" + ("/".join(["static","videos",file])))


    return all_videos + get_link_list(base_path)




def add_video_link(base_path,new_link):
    """adds the video to the linklist"""
    current_links = get_link_list(base_path=base_path)
    current_links.append(new_link)
    with open(os.path.join(base_path,"static","videos", "video_links.json"),"w") as video_links:
        json.dump(current_links,video_links,indent=4)
