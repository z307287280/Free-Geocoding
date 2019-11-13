import os
import datetime
import random
import numpy as np
import pandas as pd
import multiprocessing as mp
import glob
from geopy.geocoders import Nominatim, Photon, DataBC, ArcGIS
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


__encoder__ = [ArcGIS(timeout=100), DataBC(timeout=100)]


def to_str(text):
    # this is the encoder to decode bytes into str

    if isinstance(text, bytes):
        value = text.decode('utf-8')
    else:
        value = text
    return value


def logging_info(address):
    # this is a simple log to store the transformed physical address.

    with open('log_info.txt', 'a+') as log_info:
        log_info.write(address + '\n')
    log_info.close()


def check_point(address_list):
    # check if current address in the log

    with open('log_info.txt', 'a+') as log_info:
        remains = set(address_list) - set(log_info.read().split('\n'))
    log_info.close()
    return list(remains)


def _geo_encoder(address_list, encoder, lag, retry_sleep=300, retry_times=3):
    container = {'Address': list(), 'Latitude': list(), 'Longitude': list(), 'FAILED': list()}

    for address in address_list:
        str_address = to_str(address)

        try:
            location = encoder.geocode(str_address)
            print('[INFO] START TO TRANSFORM <<{}>>:'.format(address), end=' ')

            if location:
                container['Address'].append(str_address)
                container['Latitude'].append(location.latitude)
                container['Longitude'].append(location.longitude)
                print('COMPLETED')
            else:
                address['FAILED'].append(address)
                print('FAILED')

        except (GeocoderServiceError, GeocoderTimedOut):
            count = 0
            while count != retry_times:
                print('[INFO] ENCOUNTER ERRORS, WILL RETRY <<{}>> IN {} MINUTES'.format(address, round(retry_sleep / 60), 2))
                time.sleep(retry_sleep)

                try:
                    location = encoder.geocode(str_address)
                    print('[INFO] RESTART TO TRANSFORM <<{}>>:'.format(address), end=' ')
                    if location:
                        container['Address'].append(str_address)
                        container['Latitude'].append(location.latitude)
                        container['Longitude'].append(location.longitude)
                        print('COMPLETED')
                        break
                    else:
                        container['FAILED'].append(address)
                        print('FAILED')
                        break
                except:
                    continue
                count += 1

            else:
                print('[INFO] WILL SKIP <<{}>> SINCE RUN OUT OF MAXIMUM RETRY TIMES'.format(address))
                container['FAILED'].append(address)
                continue
        time.sleep(random.random() + lag)
    return container


def mapper(address_container, lag, n_cores):
    if n_cores > mp.cpu_count() or n_cores > len(__encoder__):
        n_cores = min(mp.cpu_count(), len(__encoder__))

    split_address = np.array_split(address_container, n_cores)
    args = [(split_address[i], __encoder__[i], lag) for i in range(n_cores)]

    p = mp.Pool(n_cores)
    split_coordinate = p.starmap(_geo_encoder, args)
    p.close()
    p.join()
    return split_coordinate


def reducer(split_coordinate):
    container = {'Address': list(), 'Latitude': list(), 'Longitude': list(), 'FAILED': list()}
    for batch in split_coordinate:
        for i in range(len(batch['Address'])):
            container['Address'].append(batch['Address'][i])
            container['Latitude'].append(batch['Latitude'][i])
            container['Longitude'].append(batch['Longitude'][i])
        container['FAILED'].extend(batch['FAILED'])
    return container


def geo_transformer(address_list, output=os.getcwd(), lag=0, batch_size=None, check_log=True, n_cores=None):
    '''
    :param address_list: the list of address needs to be transform into coordinate
    :param encoder: the encoder that uses to transform
    :param lag: sleep time
    :param retry_sleep: when a transformation fails, the time to wail until next retry
    :param retry_times: maximum retry times
    :return: return a dictionary including keys and values of 'Address', 'Latitude', 'Longitude'
    '''

    if not os.path.exists(output):
        os.makedirs(output)

    if not check_log:
        if os.path.exists('log_info.txt'):
            os.remove('log_info.txt')
        address_container = address_list
    else:
        address_container = check_point(address_list)

    if batch_size and len(address_container) // batch_size > 1.5:
        n = len(address_container) // batch_size
        n_batches = np.array_split(address_container, n)
        print(len(n_batches))
    else:
        n_batches = [address_container]

    exist_file = [file.split('\\')[-1] for file in glob.glob(output+'/coordinate_batch_*.csv')]
    for idx, batch in enumerate(n_batches):
        file_name = 'coordinate_batch_{}.csv'.format(idx+1)
        coordinate_file_name = output + '/' + file_name
        if file_name in exist_file:
            print('[INFO] FILE', file_name, 'EXIST')
            continue

        print('======================================================')
        print('[INFO] {}: START TO PROCESS BATCH {}  '.format(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                                              idx + 1))
        print('======================================================')
        if not n_cores or n_cores == 1 or len(batch) < 50:
            encoder = __encoder__[0]
            coordinate_container = _geo_encoder(batch, encoder, lag)
        else:
            split_coordinate = mapper(batch, lag, n_cores)
            coordinate_container = reducer(split_coordinate)

        failed_container = coordinate_container.pop('FAILED')
        for address in coordinate_container['Address']:
            logging_info(address)

        pd.DataFrame(coordinate_container).to_csv(coordinate_file_name)
        if failed_container:
            pd.DataFrame(failed_container).to_csv(output + '/coordinate_batch_{}_failed.csv'.format(idx + 1))
        print('[INFO] {}: FINISHED BATCH {}  '.format(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), idx + 1))

    print('======================================================')
    print('[INFO] {}: FINISHED ALL TRANSFORMATION'.format(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    print('======================================================')

