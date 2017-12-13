import matplotlib
matplotlib.use('Agg')
import numpy as np
import scipy.signal as signal
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Formating function used for the purpos of plotting with MHz
def format_mega(x, pos):
  if x >= 1e6:
    return '%3.2f' % (x/1e6)
#    return x/1e6
  else:
    return x
# Little function to join a list of strings into one string
def join(inp_list):
  out_string = ''
  for i in inp_list:
    out_string += i
  return out_string

def IQ_to_spectrogram(filename_IQ, mode):
  rate, data = wavfile.read(filename_IQ, mmap=False)
  data_cmpl = data.view(np.int16).astype(np.float32).view(np.complex64)   # Changing the data type to complex and
  data_cmpl = data_cmpl.reshape(data_cmpl.shape[0] * data_cmpl.shape[1])  # Reshaping to fit the specgram

  Fc = int(filename_IQ.split('_')[3][:-3])*1000

  cmap = plt.get_cmap('spectral')
  function_formatter = FuncFormatter(format_mega)
#  vmin = 10 * np.log10(np.max(np.abs(data_cmpl))) - 40

  color_legend, spectrogram = plt.subplots()
  Sxx,  f, t, cb = spectrogram.specgram(data_cmpl, NFFT=65536, Fs=rate, Fc=Fc, vmin=-80, vmax=-18, sides='onesided', mode=mode)
  spectrogram.set_ylabel('f [MHz]')
  spectrogram.yaxis.set_major_formatter(function_formatter)
  spectrogram.set_xlabel('t [s]')
  spectrogram.yaxis.limit_range_for_scale(0, rate)
  color_legend.colorbar(cb, label='P/f [dB/Hz]')

  x1,x2,y1,y2 = spectrogram.axis()
  spectrogram.axis((x1, x2, 435338000, 435362000)) # leave x range the same, change y (frequency) range

  plt.savefig('..' + join(filename_IQ.split('.')[:-1])+'.png', dpi=600, bbox_inches='tight', pad_inches=0.5)
  plt.close()

  return '..' + join(filename_IQ.split('.')[:-1])+'.png'
