"""P6 narration: sample-perfect boundaries, input format and overlap guards."""
import json
import wave
from pathlib import Path

import pytest
from studio.film import FilmError
from studio.voice import assemble_file, assemble_narration


def wav_file(path, seconds=1, rate=24000, channels=1, sample_width=2):
    with wave.open(str(path),"wb") as w:
        w.setnchannels(channels);w.setsampwidth(sample_width);w.setframerate(rate)
        w.writeframes(b"\x01\x04"*max(0,int(rate*seconds))*channels if sample_width==2
                      else b"\x01"*max(0,int(rate*seconds))*channels)
    return path


def film(events=None,frames=96):
    return {"fps":24,"total_frames":frames,"narration":events if events is not None
            else [{"shot_id":"s1","wav":"one.wav","absolute_frame":6,
                   "shot_end_frame":frames,"text":"hello"}]}


def test_sample_exact_assembly_and_manifest(tmp_path):
    wav_file(tmp_path/"one.wav",seconds=2)
    built=assemble_narration(film(),tmp_path,tmp_path/"audio"/"master.wav")
    assert built["sample_count"]==96000
    assert built["segments"][0]["start_sample"]==6000
    assert built["segments"][0]["end_sample"]==54000
    with wave.open(str(tmp_path/"audio"/"master.wav")) as wav:
        assert wav.getframerate()==24000 and wav.getnframes()==96000
        assert wav.readframes(6000)==b"\x00\x00"*6000
        assert wav.readframes(1)==b"\x01\x04"
    timeline=tmp_path/"film.json"
    timeline.write_text(json.dumps(film()))
    assert assemble_file(timeline,tmp_path,tmp_path/"out.wav",tmp_path/"manifest"/"voice.json").is_file()
    assert json.loads((tmp_path/"manifest"/"voice.json").read_text())==built


@pytest.mark.parametrize("invalid",[
    {"fps":30,"total_frames":96,"narration":[]},
    {"fps":24,"total_frames":0,"narration":[]},
    {"fps":24,"total_frames":"96","narration":[]},
])
def test_invalid_film_timebase(invalid,tmp_path):
    with pytest.raises(FilmError,match="Invalid fixed"):
        assemble_narration(invalid,tmp_path,tmp_path/"out.wav")


@pytest.mark.parametrize("filename",["../evil.wav","/absolute.wav","..\\bad.wav",123])
def test_unsafe_wav_names(filename,tmp_path):
    evt=film()["narration"][0]
    with pytest.raises(FilmError,match="Unsafe"):
        assemble_narration(film([{**evt,"wav":filename}]),tmp_path,tmp_path/"out.wav")


def test_missing_wav(tmp_path):
    with pytest.raises(FilmError,match="Missing"):
        assemble_narration(film(),tmp_path,tmp_path/"out.wav")


@pytest.mark.parametrize("seconds,rate,channels,width",[
    (1,44100,1,2),(1,24000,2,2),(1,24000,1,1),
])
def test_invalid_pcm_format(seconds,rate,channels,width,tmp_path):
    wav_file(tmp_path/"one.wav",seconds,rate,channels,width)
    with pytest.raises(FilmError,match="mono PCM16"):
        assemble_narration(film(),tmp_path,tmp_path/"out.wav")


def test_empty_audio(tmp_path):
    wav_file(tmp_path/"one.wav",0)
    with pytest.raises(FilmError,match="Empty"):
        assemble_narration(film(),tmp_path,tmp_path/"out.wav")


@pytest.mark.parametrize("start,end,total,errmsg",[
    (6,24,96,"overflows"),
    (90,96,96,"overflows"),
    (-1,96,96,"overflows"),
])
def test_voice_out_of_window(start,end,total,errmsg,tmp_path):
    wav_file(tmp_path/"one.wav",2)
    event={**film()["narration"][0],"absolute_frame":start,"shot_end_frame":end}
    with pytest.raises(FilmError,match=errmsg):
        assemble_narration(film([event],total),tmp_path,tmp_path/"out.wav")


def test_overlap_rejected(tmp_path):
    wav_file(tmp_path/"one.wav",2)
    wav_file(tmp_path/"two.wav",1)
    e=film()["narration"][0]
    second={**e,"wav":"two.wav","absolute_frame":15}
    with pytest.raises(FilmError,match="overlap"):
        assemble_narration(film([e,second]),tmp_path,tmp_path/"out.wav")


def test_event_free_silence_track(tmp_path):
    result=assemble_narration(film([]),tmp_path,tmp_path/"silent.wav")
    assert result["segments"]==[] and result["duration_seconds"]==4
