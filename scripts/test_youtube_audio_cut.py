import unittest
from unittest.mock import patch, MagicMock
import os
import youtube_audio_cut


class TestYouTubeAudioCut(unittest.TestCase):

    @patch('youtube_audio_cut.subprocess.run')
    def test_download_audio(self, mock_run):
        url = "https://www.youtube.com/watch?v=pz1-SJ0IJKo"
        youtube_audio_cut.download_audio(url)
        mock_run.assert_called_once_with([
            "yt-dlp",
            "-o",
            youtube_audio_cut.TMP_RAW_ORIGINAL,
            "-x",
            "--audio-format",
            "mp3",
            "--audio-quality",
            "0",
            url,
        ], check=True)

    @patch('youtube_audio_cut.subprocess.run')
    def test_cut_audio(self, mock_run):
        start_time = "00:00:10"
        end_time = "00:00:20"
        youtube_audio_cut.cut_audio(start_time, end_time)
        mock_run.assert_called_once_with([
            "ffmpeg",
            "-i",
            youtube_audio_cut.TMP_RAW_ORIGINAL,
            "-ss",
            start_time,
            "-to",
            end_time,
            youtube_audio_cut.TMP_CUT,
        ], check=True)

    @patch('youtube_audio_cut.os.remove')
    @patch('youtube_audio_cut.os.path.exists', return_value=True)
    def test_cleanup(self, mock_exists, mock_remove):
        youtube_audio_cut.cleanup()
        self.assertEqual(mock_remove.call_count, 2)
        mock_remove.assert_any_call(youtube_audio_cut.TMP_RAW_ORIGINAL)
        mock_remove.assert_any_call(youtube_audio_cut.TMP_CUT)

if __name__ == '__main__':
    unittest.main()