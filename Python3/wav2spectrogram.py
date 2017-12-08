import matplotlib
matplotlib.use('Agg')
import numpy as np
import scipy.signal as signal
import numpy as np
import scipy.signal as signal
from scipy.io import wavfile
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def format_mega(x, pos):
  if x >= 1e6:
    return '%3.2f' % (x/1e6)
#    return x/1e6
  else:
    return x

def IQ_to_spectogram(filename_IQ='semmi'):
  rate, data = wavfile.read('HDSDR_20160121_003353Z_435320kHz_RF.UD.local.wav', mmap=False)
  data_cmpl = data.view(np.int16).astype(np.float32).view(np.complex64)   # Changing the data type to complex and
  data_cmpl = data_cmpl.reshape(data_cmpl.shape[0] * data_cmpl.shape[1])  # Reshaping to fit the specgram

  cmap = plt.get_cmap('spectral')
  function_formatter = FuncFormatter(format_mega)
  vmin = 10 * np.log10(np.max(np.abs(data_cmpl))) - 40

  color_legend, spectrogram = plt.subplots()
  Sxx,  f, t, cb = spectrogram.specgram(data_cmpl, NFFT=2048, Fs=rate, Fc=435320000, vmin=-18, sides='onesided')
  spectrogram.set_ylabel('f [MHz]')
  spectrogram.yaxis.set_major_formatter(function_formatter)
  spectrogram.set_xlabel('t [s]')
#  ax.ylim(-rate/2, rate/2)
  color_legend.colorbar(cb)
  plt.savefig("NO-84.png", dpi=600, bbox_inches='tight', pad_inches=0.5)
  plt.close()
