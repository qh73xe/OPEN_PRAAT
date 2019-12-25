form reduce_noise
    text input /home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/WAV_R/1001/split/4.WAV
    text output /home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/WAV_R/1001/SS/4.WAV
endform

sound = Read from file: input$ 
selectObject: sound
To Spectrum: "yes"
freq = Get highest frequency

selectObject: sound
Reduce noise: 0, 0, 0.025, 80, 10000, freq, -20, "spectral-subtraction"
Save as WAV file: output$

select all
Remove
