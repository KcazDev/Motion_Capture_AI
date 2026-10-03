"""Camera view plus a dedicated text panel; mirroring is display-only."""
import textwrap

EDGES = ((11,12),(11,23),(12,24),(23,24),(11,13),(13,15),(12,14),(14,16),(23,25),(25,27),(24,26),(26,28))

def render(frame, landmarks, metric, state, result, count, fps, mirror=True):
    import cv2
    import numpy as np
    frame = frame.copy()
    h, w = frame.shape[:2]
    if landmarks:
        for a, b in EDGES:
            pa, pb = landmarks[a], landmarks[b]
            if min(pa.visibility, pb.visibility, pa.presence, pb.presence) >= .65:
                cv2.line(frame, (int(pa.x*w), int(pa.y*h)), (int(pb.x*w), int(pb.y*h)), (40,220,150), 3)
    if mirror:
        frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (800, 450))
    canvas = np.full((740, 1220, 3), (28, 22, 18), dtype=np.uint8)
    canvas[75:525, 20:820] = frame
    def line(text, x, y, scale=.6, color=(225,230,235)):
        cv2.putText(canvas, text, (x,y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)
    line('R-CON / MOTIONAI', 25, 42, 1)
    line('MOVEMENT ASSESSMENT', 850, 100, .6)
    line(state if metric else 'TRACKING UNCERTAIN', 850, 138, .65, (50,210,240))
    line(f'Attempts: {count}   FPS: {fps:.1f}', 850, 175)
    if metric:
        for i, text in enumerate((f'Torso lean: {metric.torso:.0f} deg', f'Knee angle: {metric.knee:.0f} deg',
                f'Hip angle: {metric.hip:.0f} deg', f'Wrist height: {metric.wrist_height:.2f} TL',
                f'Wrist reach: {metric.reach:.2f} TL', f'Hand speed: {metric.speed:.2f} TL/s')):
            line(text, 850, 215+i*32, .55)
    else:
        line('One person; full body visible.', 850, 220, .5)
        line('Keep the selected side visible.', 850, 250, .5)
    line('Stand tall to ready. Bend, lift, then stand tall again.', 25, 565)
    line('Q / Esc: exit    R: reset session    TL = torso length', 25, 600, .55)
    line('2D demo estimates; thresholds require calibration. No safety certification.', 25, 635, .52)
    if result:
        color = (80,210,100) if result['status']=='PASS' else (80,170,245)
        line('LAST ATTEMPT: '+result['status'], 850, 440, .65, color)
        lines = textwrap.wrap(' '.join(result['reasons']), 34)
        for i, text in enumerate(lines[:9]):
            line(text, 850, 477+i*25, .48)
    return canvas
