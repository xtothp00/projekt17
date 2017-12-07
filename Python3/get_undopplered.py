import re
import datetime, pytz
import os
import pymediainfo

# Function to get some information from the IQ sample filename.
def extract_IQ_filename(filename, directory='../NO-84'):
  '''extract_IQ_filename(filename, [directory='../NO-84'])

  This function is extracting the filename of which pattern
  will be the same in the future, or the REGEX needs to be changed.
  The function will return a dictionary conaning:
  *date       //YYYYMMDD//
  *time       //HHMMSS//
  *frequency  //CCCMMM//[kHz]
  *extension  //re.(\w{3})//e.g. wav
  If the file is not ending with 'wav', then instead of a dictionary
  None is returned.
  '''
#                              HDSDR_      20160126 _       205400  Z _             435320 kHz_ RF  .              wav
  pattern_named = re.compile(r'HDSDR_(?P<date>\d{8})_(?P<time>\d{6}).*_(?P<frequency>\d{6})kHz_(RF)\.(?P<extension>\w{3})$')    # REGEX pattern with named subgroups date, time, frequency, extension
  filename_regexed_named = re.search(pattern_named, filename)
  file_parameters = filename_regexed_named.groupdict()

  if file_parameters['extension'] == 'wav':     # filter out non-wav files
    return file_parameters
  else:
    return None

# A little 'key' function for sorting TLE files with sorted()
def key_function_TLE(date_IQ, date_TLEs):
  return abs(date_IQ - date_TLEs)

def find_TLE_for_IQ_file(filename_IQ, directory_TLE='../keps/'):
  '''find_TLE_for_IQ_file(filename_IQ, [directory_TLE='../keps/'])

  This function is returning the best matching TLEs file
  based on the IQ filename given and the date encoded in it.
  The best match means the least difference between the dates
  indicated by the names of the TLEs and IQ files.
  '''
  parameters_IQ = extract_IQ_filename(filename_IQ)
  if parameters_IQ != None:

    date_IQ = datetime.datetime.strptime(parameters_IQ.get('date'), '%Y%m%d')
    directory_path_TLEs = os.path.join(directory_TLE, str(date_IQ.year))
    pattern_TLE_file = re.compile('%d-%02d-' % (date_IQ.year, date_IQ.month))
    TLEs = list()     # Empty list for TLEs file

    for i in os.listdir(directory_path_TLEs):
      if bool(re.search(pattern_TLE_file, i)):
        TLEs.append(i)
    TLEs = sorted(TLEs, key=lambda TLE: abs(date_IQ - datetime.datetime.strptime(TLE[:10], '%Y-%m-%d')))

    return TLEs[0]
  else:
    return None

def undoppler_it(filename_IQ, satellite_name='NO-84', satellite_frequency='435350000', directory_IQ='../NO-84', directory_TLE='../keps', location_SDR='lat=49.173238,lon=16.961292,alt=263.73'):
  filename_TLE = find_TLE_for_IQ_file(filename_IQ, directory_TLE)

  if filename_TLE != None:
    parameters_IQ = extract_IQ_filename(filename_IQ)
    mediainfo_IQ  = pymediainfo.MediaInfo.parse(os.path.join(directory_IQ, filename_IQ))
    mediainfo_IQ_tracks = mediainfo_IQ.tracks
    audio = mediainfo_IQ_tracks[1]
    audio_dict = audio.to_data()

    local_TZ = pytz.timezone('Europe/Prague')
    naive_datetime_IQ = datetime.datetime.strptime(parameters_IQ.get('date') + parameters_IQ.get('time'), '%Y%m%d%H%M%S')
    local_datetime_IQ = local_TZ.localize(naive_datetime_IQ, is_dst=None)
    utc_datetime_IQ = local_datetime_IQ.astimezone(pytz.utc)

    samplerate = '--samplerate ' + str(audio_dict.get('sampling_rate')) + ' '
    if (int(audio_dict.get('resolution')) == 16) & (audio_dict.get('format_settings') == 'Little / Signed'):
      intype   = '--intype i16 '
      outtype  = '--outtype i16 '
      sox_cmd = 'sox --bits 16 --channels 2 --encoding signed-integer --rate ' + str(audio_dict.get('sampling_rate')) + ' --type raw - --bits 16 --channels 2 --encoding signed-integer --rate ' + str(audio_dict.get('sampling_rate')) + ' --type wav -'
    else:           #in case of strange Wave format, e.g. float samples
      print('Format yet not tested: ')
      print(' * reslution:      ', audio_dict.get('resolution'))
      print(' * format_settings:', audio_dict.get('format_settings'))
      return 1
    tlefile    = '--tlefile '   + os.path.join(directory_TLE, filename_TLE[:4], filename_TLE) + ' '
    tlename    = '--tlename '   + satellite_name                     + ' '
    location   = '--location '  + location_SDR                       + ' '
    frequency  = '--frequency ' + satellite_frequency                + ' '
    time       = '--time '      + local_datetime_IQ.isoformat()[:-6] + ' '
    infile     = os.path.join(directory_IQ, filename_IQ)             + ' '
    output     = ' > '
    for i in filename_IQ.split('.')[:-1]:
      output  += i
    output    += '.UD.local.' + filename_IQ.split('.')[-1]

    doppler_cmd = 'doppler track '+ samplerate + intype + outtype + tlefile + tlename + location + frequency + time

    full_command_doppler = 'cat ' + infile + ' | ' + doppler_cmd + ' | ' + sox_cmd + output

    print(full_command_doppler)
    os.system(full_command_doppler)
    print(full_command_doppler)
# cat ../../../test/HDSDR_20160127_161858Z_435320kHz_RF.wav  | doppler track --samplerate 250000 --intype i16 --outtype i16 --tlefile ../keps/2016/2016-01-21.amsat.tle --tlename NO-84 --location lat=49.173238,lon=16.961292,alt=263.73 --frequency 435320000 --time 2016-01-21T00:33:53 | sox --bits 16 --channels 2 --encoding signed-integer --rate 96000 -t raw - --type wav - > HDSDR_20160121_003353Z_435320kHz_RF.UD.local.wav
#
#Doppler tracking mode
#
#USAGE:
#        doppler track [FLAGS] [OPTIONS] --samplerate <SAMPLERATE> --intype <INTYPE> --tlefile <TLEFILE> --tlename <TLENAME> --location <LOCATION> --frequency <FREQUENCY>
#
#FLAGS:
#    -h, --help       Prints help information
#    -V, --version    Prints version information
#
#OPTIONS:
#        --frequency <FREQUENCY>      Satellite transmitter frequency in Hz
#    -i, --intype <INTYPE>            IQ data type [values: i16, f32]
#        --location <LOCATION>        Observer location (lat=<deg>,lon=<deg>,alt=<m>): eg. lat=58.64560,lon=23.15163,alt=8
#        --offset <OFFSET>            Constant frequency shift in Hz. Can be used to compensate constant offset
#    -o, --outtype <OUTTYPE>          IQ data output type [values: i16, f32]
#    -s, --samplerate <SAMPLERATE>    IQ data samplerate
#        --time <TIME>                Observation start time in UTC Y-m-dTH:M:S: eg. 2015-05-13T14:28:48. If not specified current time is used
#    --tlefile <TLEFILE>          TLE file: eg. http://www.celestrak.com/NORAD/elements/cubesat.txt
#    --tlename <TLENAME>          TLE name in TLE file: eg. ESTCUBE 1
#

  else:
    return None
