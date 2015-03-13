import sys
import pjsua as pj
import time
import wave
import contextlib

def log_cb(level, str, len):
    print str,

class MyCallCallback(pj.CallCallback):
    in_call = False
	
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    def on_state(self):
        print "Call is ", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"
        
    def silence_block(self, call_slot):
        tx, rx = lib.conf_get_signal_level(call_slot)
        print "Waiting for Voice"
        t = 0
        while rx < 0.1 and self.call.info().state != pj.CallState.DISCONNECTED and t < 100:
           	tx, rx = lib.conf_get_signal_level(call_slot)
           	print "blocking", tx, rx
           	time.sleep(0.05)
           	t = t + 1
        print "Voice found..."
    
    def play_audio(self, filename, call_slot, rec_slot):
    	#hook up the call slot to the player
    	print filename
    	audio = lib.create_player(filename) 
    	time.sleep(1)
        lib.conf_connect(call_slot, lib.player_get_slot(audio))
    	lib.conf_connect(lib.player_get_slot(audio), call_slot)
    	
		#hook up the player to the recorder
    	lib.conf_connect(lib.player_get_slot(audio), rec_slot)
    	lib.conf_connect(rec_slot, lib.player_get_slot(audio))
    	
    	with contextlib.closing(wave.open(filename,'r')) as f:
    	    	frames = f.getnframes()
    	    	rate = f.getframerate()
    	    	duration = frames / float(rate)
    	    	print "Playing audio now? sleeping for %f seconds!" % duration
    	    	time.sleep(duration)
    	
    	#disconnect shit
    	#lib.conf_disconnect(call_slot, lib.player_get_slot(audio))
    	#lib.conf_disconnect(lib.player_get_slot(audio), call_slot)
    	#lib.conf_disconnect(lib.player_get_slot(audio), rec_slot)
    	#lib.conf_disconnect(rec_slot, lib.player_get_slot(audio))
    	self.silence_block(call_slot) 

    def on_state(self):
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"
        
        if self.call.info().state == pj.CallState.DISCONNECTED:
            print 'Current call is', current_call
        if self.call.info().state == pj.CallState.CONFIRMED and self.in_call == False:
            call_slot = self.call.info().conf_slot
            self.in_call = True
            
            recorder = lib.create_recorder("recorder.wav")
            lib.conf_connect(lib.recorder_get_slot(recorder), call_slot)
            lib.conf_connect(call_slot, lib.recorder_get_slot(recorder))
            for i in range(1, 15):
            	fn = "./sounds/%d.wav" % i
            	self.play_audio(fn, call_slot, lib.recorder_get_slot(recorder))
            
            self.play_audio("./sounds/rickroll.wav", call_slot, lib.recorder_get_slot(recorder))
            lib.hangup_all()

if len(sys.argv) != 2:
    print "Usage: lenny.py sip:EXTENSION_NUMBER@HOST:PORT"
    sys.exit(1)

try:
    lib = pj.Lib()
    media_config = pj.MediaConfig()
    media_config.no_vad = True
    lib.init(media_cfg = media_config, log_cfg = pj.LogConfig(level=3, callback=log_cb))
    transport = lib.create_transport(pj.TransportType.UDP)
    lib.start()
    #acc = lib.create_account_for_transport(transport) #anon
    acc = lib.create_account(pj.AccountConfig("1.2.3.4", "998", "")) #register with server
    call = acc.make_call(sys.argv[1], MyCallCallback())
    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
    sys.exit(1)