form create_textgrid
    text input /home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/WAV_R/1001/SS/4.WAV
    text output /home/qh73xe/Documents/corpora/realTimeMRI/20171225/Asai/TextGrid/4.TextGrid
endform

sound = Read from file: input$ 
To TextGrid (silences): 100, 0, -25, 0.1, 0.1, "#", ""
Duplicate tier: 1, 1, "IPU"
Save as text file: output$

select all
Remove