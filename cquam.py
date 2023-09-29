#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Motorola CQUAM v1.5
# Author: jowijo
# Description: Working implementation of AM Stereo
# GNU Radio version: 3.8.2.0

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import osmosdr
import time


class cquam(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Motorola CQUAM v1.5")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 44100
        self.hackrf_rate = hackrf_rate = 640000
        self.bandwidth = bandwidth = 12.e3

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_2 = filter.rational_resampler_ccf(
                interpolation=hackrf_rate,
                decimation=samp_rate,
                taps=[],
                fractional_bw=0)
        self.osmosdr_sink_0_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_sink_0_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0_0.set_sample_rate(hackrf_rate)
        self.osmosdr_sink_0_0.set_center_freq(1570e3, 0)
        self.osmosdr_sink_0_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0_0.set_gain(6, 0)
        self.osmosdr_sink_0_0.set_if_gain(44, 0)
        self.osmosdr_sink_0_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0_0.set_antenna('', 0)
        self.osmosdr_sink_0_0.set_bandwidth(bandwidth, 0)
        self.low_pass_filter_0 = filter.interp_fir_filter_ccf(
            1,
            firdes.low_pass(
                0.3,
                samp_rate,
                bandwidth,
                100,
                firdes.WIN_BLACKMAN,
                6.76))
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_add_xx_3 = blocks.add_vff(1)
        self.blocks_add_xx_1 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_source_0_0 = audio.source(44100, 'tx_source', False)
        self.analog_sig_source_x_2_0_0 = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, 25, 0.09, 0, 0)
        self.analog_sig_source_x_2_0 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 0, 1, 0, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_2_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_2_0_0, 0), (self.blocks_add_xx_3, 0))
        self.connect((self.audio_source_0_0, 1), (self.blocks_add_xx_1, 0))
        self.connect((self.audio_source_0_0, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.audio_source_0_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.audio_source_0_0, 1), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_add_xx_3, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_add_xx_3, 1))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_2, 0))
        self.connect((self.rational_resampler_xxx_2, 0), (self.osmosdr_sink_0_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_2_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_2_0_0.set_sampling_freq(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(0.3, self.samp_rate, self.bandwidth, 100, firdes.WIN_BLACKMAN, 6.76))

    def get_hackrf_rate(self):
        return self.hackrf_rate

    def set_hackrf_rate(self, hackrf_rate):
        self.hackrf_rate = hackrf_rate
        self.osmosdr_sink_0_0.set_sample_rate(self.hackrf_rate)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.low_pass_filter_0.set_taps(firdes.low_pass(0.3, self.samp_rate, self.bandwidth, 100, firdes.WIN_BLACKMAN, 6.76))
        self.osmosdr_sink_0_0.set_bandwidth(self.bandwidth, 0)





def main(top_block_cls=cquam, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
