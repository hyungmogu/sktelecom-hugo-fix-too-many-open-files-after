import psutil
import time
import os, os.path
import subprocess, signal
import unittest

class TestHugoStart(unittest.TestCase):
  def setUp(self) -> None:
    dirPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    executable = "start.sh"
    timeout = 10

    # Because windows use sh command to compile bash script: https://stackoverflow.com/questions/26522789/how-to-run-sh-on-windows-command-prompt#answer-30744390
    if os.name == "nt":
      self.proc = subprocess.Popen(["sh", os.path.join(dirPath, executable)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
      self.proc = subprocess.Popen(["bash", os.path.join(dirPath, executable)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # This solution because microsoft server hangs when running test: https://stackoverflow.com/questions/48763362/python-subprocess-kill-with-timeout#answer-48763628
    # Resource warning expected
    for _ in range(timeout):
      if self.proc.poll() is not None:
        break
      time.sleep(1)
    else:
      parent = psutil.Process(self.proc.pid)
      for child in parent.children(recursive=True):
        os.kill(child.pid, signal.SIGTERM)
      os.kill(parent.pid, signal.SIGTERM)

    self.timeExpOut = "".join([x.decode() for x in self.proc.stdout]).strip().lower()
    self.timeExpErr = "".join([x.decode() for x in self.proc.stderr]).strip().lower()

    print("--------------Out----------------")
    print(self.timeExpOut)
    print("--------------Err----------------")
    print(self.timeExpErr)


  def test_start_command_should_not_return_error (self) -> None:
    expected = True

    if len(self.timeExpErr) == 0:
      result = True
    else:
      result = False

    self.assertEqual(expected, result)

  def test_start_command_should_not_include_any_errors_in_output (self) -> None:
    expected = False
    result = self.timeExpOut.find( "error:") != -1
    self.assertEqual(expected, result)

  def test_start_command_should_show_web_server_is_starting (self) -> None:
    expected = True

    if len(self.timeExpOut) == 0:
      result = False
    else:
      result = self.timeExpOut.find( "web server is available at //localhost:") != -1

    self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()