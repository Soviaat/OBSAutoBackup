import obspython as obs
import os
import shutil
from datetime import datetime

MIN_BACKUPS = 3        
DEFAULT_MAX_BACKUPS = 5  
MAX_BACKUPS_LIMIT = 30   

minecraft_world_path = ""
backup_parent_path = ""
max_backups = DEFAULT_MAX_BACKUPS
backup_trigger_event = "stop_recording"
script_enabled = False

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def list_backup_files(backup_path):
    backup_files = []
    for root, dirs, files in os.walk(backup_path):
        for file in files:
            if file.endswith(".zip"):
                backup_files.append(os.path.join(root, file))
    backup_files.sort()
    return backup_files

def backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups):
    if not script_enabled:
        return

    if not minecraft_world_path:
        obs.script_log(obs.LOG_WARNING,"You haven't specified the path to your Minecraft world.")
        return

    if not backup_parent_path:
        obs.script_log(obs.LOG_WARNING, "You haven't specified a backup folder.")
        return

    world_folder_name = os.path.basename(minecraft_world_path)
    world_backup_path = os.path.join(backup_parent_path, world_folder_name)

    if not os.path.exists(world_backup_path):
        os.makedirs(world_backup_path)

    files = list_backup_files(world_backup_path)

    if len(files) >= max_backups:
        oldest_file = files.pop(0)
        obs.script_log(obs.LOG_INFO, f"Oldest backup has been deleted: {oldest_file}")
        os.remove(oldest_file)

    timestamp = get_timestamp()
    backup_filename = os.path.join(world_backup_path, f"{world_folder_name}_backup_{timestamp}.zip")

    shutil.make_archive(os.path.splitext(backup_filename)[0], 'zip', minecraft_world_path)
    obs.script_log(obs.LOG_INFO, f"{world_folder_name} backup has been successfully created: {backup_filename}")

def on_event(event):
    global backup_parent_path
    global max_backups
    global backup_trigger_event

    if not script_enabled:
        return

    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED and backup_trigger_event == "stop_streaming":
        backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups)
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED and backup_trigger_event == "stop_recording":
        backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups)

def script_description():
    return f"Creates a backup of the specified Minecraft world after clicking the \"Stop Streaming/Recording\" button, keeping a minimum of 3 and a maximum of 30 backups."

def script_properties():

    props = obs.obs_properties_create()
    

    checkbox = obs.obs_properties_add_bool(props, "script_enabled", "Enable/disable script")
    obs.obs_property_set_long_description(checkbox, "Checked when on, unchecked when off.")
    
    obs.obs_properties_add_path(props, "minecraft_world_path", "Path to world folder:", obs.OBS_PATH_DIRECTORY, "", None)
    obs.obs_properties_add_path(props, "backup_parent_path", "Path to backup folder:", obs.OBS_PATH_DIRECTORY, "", None)
    obs.obs_properties_add_int_slider(props, "max_backups", "Number of maximum backups", MIN_BACKUPS, MAX_BACKUPS_LIMIT, 1)

    backup_event_menu = obs.obs_properties_add_list(props, "backup_trigger_event", "Make backup on:", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(backup_event_menu, "Stop Streaming", "stop_streaming")
    obs.obs_property_list_add_string(backup_event_menu, "Stop Recording", "stop_recording")
    obs.obs_property_set_long_description(backup_event_menu, "Choose when to make a backup of your world.")
    
    return props

def script_update(settings):
    global minecraft_world_path
    global backup_parent_path
    global max_backups
    global backup_trigger_event
    global script_enabled

    script_enabled = obs.obs_data_get_bool(settings, "script_enabled")
    minecraft_world_path = obs.obs_data_get_string(settings, "minecraft_world_path")
    backup_parent_path = obs.obs_data_get_string(settings, "backup_parent_path")
    max_backups = obs.obs_data_get_int(settings, "max_backups")
    backup_trigger_event = obs.obs_data_get_string(settings, "backup_trigger_event")

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)