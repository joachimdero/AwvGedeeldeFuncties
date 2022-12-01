import platform
import time

from termcolor import colored

from VKB.FSConnector import FSConnector

from VKB.JsonToVkbFeatureProcessor import JsonToVkbFeatureProcessor
from VKB.OTLMOW_Helpers.RequesterFactory import RequesterFactory
from VKB.SettingsManager import SettingsManager

if __name__ == '__main__':
    if platform.system() == 'Linux':
        OTLMOW_settings_path = '/home/davidlinux/Documents/AWV/resources/settings_OTLMOW.json'
        this_settings_path = 'settings_OTLMOW_linux.json'
    else:
        OTLMOW_settings_path = 'C:\\resources\\settings_OTLMOW.json'
        this_settings_path = 'C:\\resources\\settings_AWVGedeeldeFuncties.json'

    # een aantal classes uit OTLMOW library gebruiken
    settings_manager = SettingsManager(settings_path=this_settings_path)
    requester = RequesterFactory.create_requester(settings=settings_manager.settings, auth_type='cert', env='prd')

    # haal x aantal afschermende constructies uit de feature server
    fs_c = FSConnector(requester)
    start = time.time()
    print(colored(f'Connecting to Feature server...', 'green'))
    raw_output = fs_c.get_raw_lines(layer="verkeersborden", lines=1000)  # beperkt tot X aantal lijnen
    end = time.time()
    print(colored(f'Number of lines (verkeersborden) from Feature server: {len(raw_output)}', 'green'))
    print(colored(f'Time to get input from feature server: {round(end - start, 2)}', 'yellow'))

    processor = JsonToVkbFeatureProcessor()
    features = processor.process_json_object_to_vkb_features(raw_output)

    borden = []
    for f in features:
        borden.extend(f.borden)

    vormen = set(map(lambda b: b.bord_code, borden))

    print(vormen)
