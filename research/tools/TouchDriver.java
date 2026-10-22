package io.github.meiyongai.toki.touch;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Random;

public class TouchDriver {
    private static final String DEV = "/dev/input/event3";
    private static final short EV_SYN = 0;
    private static final short SYN_REPORT = 0;
    private static final short EV_KEY = 1;
    private static final short BTN_TOUCH = 330;
    private static final short EV_ABS = 3;
    private static final short ABS_MT_SLOT = 47;
    private static final short ABS_MT_TOUCH_MAJOR = 48;
    private static final short ABS_MT_TOUCH_MINOR = 49;
    private static final short ABS_MT_POSITION_X = 53;
    private static final short ABS_MT_POSITION_Y = 54;
    private static final short ABS_MT_TRACKING_ID = 57;

    private static void writeEvent(FileOutputStream fos, ByteBuffer buf, short type, short code, int value) throws IOException {
        buf.clear();
        buf.putInt(0); // tv_sec
        buf.putInt(0); // tv_usec
        buf.putShort(type);
        buf.putShort(code);
        buf.putInt(value);
        fos.write(buf.array());
    }

    private static void syn(FileOutputStream fos, ByteBuffer buf) throws IOException {
        writeEvent(fos, buf, EV_SYN, SYN_REPORT, 0);
        fos.flush();
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: TouchDriver swipe <x1> <y1> <x2> <y2> <duration_ms> | tap <x> <y>");
            return;
        }

        String action = args[0];
        try (FileOutputStream fos = new FileOutputStream(DEV)) {
            ByteBuffer buf = ByteBuffer.allocate(16).order(ByteOrder.LITTLE_ENDIAN);
            Random rng = new Random();
            int trackId = rng.nextInt(60000) + 1000;

            if ("tap".equalsIgnoreCase(action)) {
                int x = Integer.parseInt(args[1]);
                int y = Integer.parseInt(args[2]);

                // Down
                writeEvent(fos, buf, EV_ABS, ABS_MT_SLOT, 0);
                writeEvent(fos, buf, EV_ABS, ABS_MT_TRACKING_ID, trackId);
                writeEvent(fos, buf, EV_KEY, BTN_TOUCH, 1);
                writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_X, x);
                writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_Y, y);
                writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MAJOR, 45);
                writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MINOR, 35);
                syn(fos, buf);

                Thread.sleep(rng.nextInt(35) + 65);

                // Up
                writeEvent(fos, buf, EV_ABS, ABS_MT_TRACKING_ID, -1);
                writeEvent(fos, buf, EV_KEY, BTN_TOUCH, 0);
                syn(fos, buf);

                System.out.println("TAP_SUCCESS (" + x + "," + y + ")");
            } else if ("swipe".equalsIgnoreCase(action)) {
                double x1 = Double.parseDouble(args[1]);
                double y1 = Double.parseDouble(args[2]);
                double x2 = Double.parseDouble(args[3]);
                double y2 = Double.parseDouble(args[4]);
                int durationMs = Integer.parseInt(args[5]);

                // Construct natural human right-thumb cubic Bezier curve
                double cp1_x = x1 - (40 + rng.nextDouble() * 40);
                double cp1_y = y1 - (200 + rng.nextDouble() * 120);
                double cp2_x = x2 + (20 + rng.nextDouble() * 40);
                double cp2_y = y2 + (180 + rng.nextDouble() * 120);

                int frameIntervalMs = 16; // 60Hz
                int numFrames = Math.max(10, durationMs / frameIntervalMs);

                // Initial DOWN
                writeEvent(fos, buf, EV_ABS, ABS_MT_SLOT, 0);
                writeEvent(fos, buf, EV_ABS, ABS_MT_TRACKING_ID, trackId);
                writeEvent(fos, buf, EV_KEY, BTN_TOUCH, 1);
                writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_X, (int) Math.round(x1));
                writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_Y, (int) Math.round(y1));
                writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MAJOR, 35);
                writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MINOR, 28);
                syn(fos, buf);

                Thread.sleep(frameIntervalMs);

                for (int i = 1; i <= numFrames; i++) {
                    double t = (double) i / numFrames;
                    // Ease-in ease-out smoothing
                    double easedT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

                    // Cubic Bezier interpolation
                    double u = 1 - easedT;
                    double tt = easedT * easedT;
                    double uu = u * u;
                    double uuu = uu * u;
                    double ttt = tt * easedT;

                    double curX = uuu * x1 + 3 * uu * easedT * cp1_x + 3 * u * tt * cp2_x + ttt * x2;
                    double curY = uuu * y1 + 3 * uu * easedT * cp1_y + 3 * u * tt * cp2_y + ttt * y2;

                    // Add subtle physiological micro-tremor
                    curX += (rng.nextGaussian() * 1.2);
                    curY += (rng.nextGaussian() * 1.2);

                    // Dynamic contact ellipse deformation
                    // Starts light (~35), compresses to peak (~115), tapers off (~40)
                    double deform = Math.sin(t * Math.PI);
                    int major = (int) (35 + deform * 80);
                    int minor = (int) (major / (1.20 + rng.nextDouble() * 0.12));

                    writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_X, (int) Math.round(curX));
                    writeEvent(fos, buf, EV_ABS, ABS_MT_POSITION_Y, (int) Math.round(curY));
                    writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MAJOR, major);
                    writeEvent(fos, buf, EV_ABS, ABS_MT_TOUCH_MINOR, minor);
                    syn(fos, buf);

                    Thread.sleep(frameIntervalMs);
                }

                // Final UP (lift-off)
                writeEvent(fos, buf, EV_ABS, ABS_MT_TRACKING_ID, -1);
                writeEvent(fos, buf, EV_KEY, BTN_TOUCH, 0);
                syn(fos, buf);

                System.out.println("SWIPE_SUCCESS " + numFrames + " frames (" + durationMs + "ms)");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
