import obspython as obs
import os
import shutil
from datetime import datetime

MIN_BACKUPS = 3            # Smallest backup limit
DEFAULT_MAX_BACKUPS = 5    # Default backup limit
MAX_BACKUPS_LIMIT = 30     # Largest backup limit

minecraft_world_path = ""
backup_parent_path = ""
max_backups = DEFAULT_MAX_BACKUPS
backup_trigger_event = "stop_recording"

# Timestamp for backup file name
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Sorting backup files by timestamp
def list_backup_files(backup_path):
    backup_files = []
    for root, dirs, files in os.walk(backup_path):
        for file in files:
            if file.endswith(".zip"):
                backup_files.append(os.path.join(root, file))
    backup_files.sort()
    return backup_files

# Backup function
def backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups):
    if not minecraft_world_path:
        obs.script_log(obs.LOG_WARNING, "A Minecraft világ mappáját nem adtad meg.")
        return

    if not backup_parent_path:
        obs.script_log(obs.LOG_WARNING, "A backup mappát nem adtad meg.")
        return

    world_folder_name = os.path.basename(minecraft_world_path)
    world_backup_path = os.path.join(backup_parent_path, world_folder_name)

    if not os.path.exists(world_backup_path):
        os.makedirs(world_backup_path)

    files = list_backup_files(world_backup_path)

    if len(files) >= max_backups:
        oldest_file = files.pop(0)
        obs.script_log(obs.LOG_INFO, f"Legrégebbi backup törölve: {oldest_file}")
        os.remove(oldest_file)

    timestamp = get_timestamp()
    backup_filename = os.path.join(world_backup_path, f"{world_folder_name}_backup_{timestamp}.zip")

    shutil.make_archive(os.path.splitext(backup_filename)[0], 'zip', minecraft_world_path)
    obs.script_log(obs.LOG_INFO, f"{world_folder_name} backup sikeresen elkészült: {backup_filename}")

# Callback when stream is stopped
def on_event(event):
    global backup_parent_path
    global max_backups
    global backup_trigger_event

    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED and backup_trigger_event == "stop_streaming":
        backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups)
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED and backup_trigger_event == "stop_recording":
        backup_minecraft_world(minecraft_world_path, backup_parent_path, max_backups)

# Script init
def script_description():
    return f"A 'Stop Streaming' gomb megnyomása után backupot készít a megadott Minecraft világról, állítható számú (minmax 3-30) backup megtartásával."

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_path(props, "minecraft_world_path", "Világ mappájának útvonala:", obs.OBS_PATH_DIRECTORY, "", None)
    obs.obs_properties_add_path(props, "backup_parent_path", "Backup mappa útvonala:", obs.OBS_PATH_DIRECTORY, "", None)
    obs.obs_properties_add_int(props, "max_backups", "Maximum backupok száma:", MIN_BACKUPS, MAX_BACKUPS_LIMIT, 1)

    backup_event_menu = obs.obs_properties_add_list(props, "backup_trigger_event", "Készítsen backupot ha:", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(backup_event_menu, "Élő adást leállítom", "stop_streaming")
    obs.obs_property_list_add_string(backup_event_menu, "Felvételt leállítom", "stop_recording")
    obs.obs_property_set_long_description(backup_event_menu, "Válaszd ki, hogy mikor készítsen backupot a Minecraft világról.")
    
    return props

def script_update(settings):
    global minecraft_world_path
    global backup_parent_path
    global max_backups
    global backup_trigger_event

    minecraft_world_path = obs.obs_data_get_string(settings, "minecraft_world_path")
    backup_parent_path = obs.obs_data_get_string(settings, "backup_parent_path")
    max_backups = obs.obs_data_get_int(settings, "max_backups")
    backup_trigger_event = obs.obs_data_get_string(settings, "backup_trigger_event")

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)