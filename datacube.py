import file
import image_process
import os

class DataCube:
    _use_cupy = False
    try:
        import cupy as cp
        _use_cupy = True
    except ImportError:
        _use_cupy = False

    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_img = None
        self.img = None
        self.center = None
        self.azavg = None
        self.azvar = None

    def ready(self):
        self.raw_img, self.img = file.load_mrc_img(self.file_path)

    def release(self):
        self.raw_img, self.img = None, None

    def calculate_center(self, intensity_range, step_size):
        self.center = list(image_process.calculate_center_gradient(self.img, intensity_range, step_size))
        return self.center

    def calculate_azimuthal_average(self):
        if self.center is None:
            raise Exception("You need to calculate center first")

        if DataCube._use_cupy:
            self.azavg, self.azvar = image_process.calculate_azimuthal_average_cuda(self.raw_img, self.center)
        else:
            self.azavg, self.azvar = image_process.calculate_azimuthal_average(self.raw_img, self.center)
        return self.azavg, self.azvar

    def save_azimuthal_data(self, intensity_start, intensity_end, intensity_slice, imageView=None):
        if self.center is None:
            self.calculate_center((intensity_start, intensity_end), intensity_slice)
        if self.azavg is None:
            self.calculate_azimuthal_average()

        i_list = [intensity_start,intensity_end,intensity_slice]
        file.save_current_azimuthal(self.azavg, self.file_path, True,  i_slice=i_list) # todo: seperate method
        file.save_current_azimuthal(self.azvar, self.file_path, False, i_slice=i_list)

        folder_path, file_full_name = os.path.split(self.file_path)
        file_name, ext = os.path.splitext(file_full_name)

        if imageView is not None:
            img_file_path = os.path.join(folder_path, file.analysis_folder_name, file_name+"_img.tiff")
            self.imgPanel.imageView.export(img_file_path)