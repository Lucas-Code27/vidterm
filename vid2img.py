import cv2

def convert_video_to_images(path):
    output_folder = "frames/"

    cap = cv2.VideoCapture(filename=path)
    count = 0

    success = True

    while success:
        success, frame = cap.read()

        if not success:
            return False

        count += 1
        cv2.imwrite(output_folder + f"frame_{count:08d}.png", frame)

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ ==  "__main__":
    convert_video_to_images("video/video.mp4")