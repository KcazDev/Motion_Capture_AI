import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from src.assessment.scoring import load_rules, score
from src.assessment.movement_metrics import Metrics, MetricTracker
from src.assessment.lift_analyzer import LiftAnalyzer
from src.vision.landmark_utils import angle
from src.vision.camera import Camera

class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules()

    def metric(self, t=0, knee=170, torso=10, height=0):
        return Metrics(t, torso, knee, 150, height, .4, .3, 'left')

    def test_geometry(self):
        self.assertAlmostEqual(angle((1,0),(0,0),(0,1)), 90)
        with self.assertRaises(ValueError):
            angle((0,0),(0,0),(1,1))

    def test_pass_fail_and_insufficient(self):
        samples = [self.metric(knee=130) for _ in range(20)]
        self.assertEqual(score(samples,self.rules)['status'], 'PASS')
        self.assertEqual(score([self.metric(torso=70) for _ in range(20)],self.rules)['status'], 'FAIL')
        self.assertEqual(score([],self.rules)['status'], 'UNASSESSED')

    def drive(self, analyzer, start, end, **values):
        results = []
        for i in range(start,end):
            t = i/10
            result = analyzer.update(self.metric(t, **values), t)
            if result:
                results.append(result)
        return results

    def test_complete_lift_exactly_once(self):
        a = LiftAnalyzer(self.rules)
        self.drive(a,0,10)
        self.assertEqual(a.state,'READY')
        self.drive(a,10,20,knee=130,height=-.5)
        results = self.drive(a,20,40,height=.2)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0]['status'],'PASS')

    def test_tracking_loss_and_reacquisition(self):
        a = LiftAnalyzer(self.rules)
        self.drive(a,0,10)
        self.drive(a,10,20,knee=130)
        result = a.update(None,2.3)
        self.assertEqual(result['status'],'UNASSESSED')
        self.assertEqual(a.state,'CALIBRATING')
        self.assertIsNone(a.update(self.metric(2.4),2.4))

    def test_camera_stall_invalidates_even_when_next_pose_valid(self):
        a = LiftAnalyzer(self.rules)
        self.drive(a,0,10)
        self.drive(a,10,20,knee=130)
        self.assertEqual(a.update(self.metric(3),3)['status'],'UNASSESSED')

    def test_standing_never_creates_attempt(self):
        self.assertEqual(self.drive(LiftAnalyzer(self.rules),0,100),[])

    def test_timeout(self):
        a = LiftAnalyzer(self.rules)
        self.drive(a,0,10)
        results = self.drive(a,10,200,knee=130)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0]['status'],'UNASSESSED')

    def test_low_confidence_and_offscreen(self):
        tracker = MetricTracker()
        landmarks = [SimpleNamespace(x=.5,y=.5,visibility=.1,presence=1) for _ in range(33)]
        self.assertIsNone(tracker.update(landmarks,(720,1280,3),0))
        landmarks[11].x = float('nan')
        self.assertIsNone(tracker.update(landmarks,(720,1280,3),1))

    def test_metric_aspect_ratio(self):
        p = [SimpleNamespace(x=.5,y=.5,visibility=1,presence=1) for _ in range(33)]
        for idx,x,y in ((11,.5,.2),(23,.5,.4),(25,.5,.6),(27,.5,.8),(15,.6,.4)):
            p[idx].x,p[idx].y=x,y
        metric=MetricTracker().update(p,(1000,2000,3),0)
        self.assertAlmostEqual(metric.knee,180)
        self.assertAlmostEqual(metric.reach,1)

    def test_backend_fallback_and_cleanup(self):
        import numpy as np
        bad, good = MagicMock(), MagicMock()
        bad.isOpened.return_value = True
        bad.read.return_value = (False,None)
        good.isOpened.return_value = True
        frame = np.zeros((2,2,3),dtype=np.uint8)
        good.read.return_value = (True,frame)
        with patch('platform.system',return_value='Windows'), patch('cv2.VideoCapture',side_effect=[bad,good]):
            with Camera() as camera:
                self.assertIs(camera.read(),frame)
            bad.release.assert_called_once()
            good.release.assert_called_once()

if __name__ == '__main__':
    unittest.main()
