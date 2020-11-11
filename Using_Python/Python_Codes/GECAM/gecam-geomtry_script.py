import os
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.patches import Polygon
from moviepy.editor import VideoClip
import numpy as np
from scipy.interpolate import interp1d
import astropy.units as u
from astropy.time import Time
from astropy.io import fits
from astropy.coordinates import SkyCoord,get_sun,get_body_barycentric
from astropy.coordinates import cartesian_to_spherical,spherical_to_cartesian
import pandas as pd
from spherical_geometry.polygon import SphericalPolygon

class Detectors(object):

    def __init__(self,name='a'):
        az = np.array([0,40,40,40,40,40,40,73.5,73.5,73.5,73.5,73.5,73.5,73.5,73.5,73.5,73.5,90,90,90,90,90,90,90,90])*u.deg
        zen = np.array([0,332.17,278.67,225.17,152.17,98.67,45.17,350.5,314.5,278.5,242.5,206.5,170.5,134.5,98.5,62.5,26.5,0,305,270,215,180,125,90,35])*u.deg
        self.detetor_vector = np.array(spherical_to_cartesian(1,90*u.deg-az,zen)).T
        name_list = []
        for i in range(len(az)):
            name_list.append(name+str(i))
        self.name = np.array(name_list)
        self.eff_angle = np.array([60]*25)

    def __call__(self, name):

        n_index = np.where(self.name == name)[0]
        detector_vector = self.detetor_vector[n_index]
        return detector_vector[0]

    def get_eff_angle(self,name):

        n_index = np.where(self.name == name)[0]
        eff_angle = self.eff_angle[n_index]
        return eff_angle[0]

    def get_names(self):
        return self.name

class Clock(object):

    def __init__(self,time_origin = None):

        if time_origin is None:
            self.time_origin_gps = Time('2019-01-01T00:00:00',format='fits',scale='utc').gps
        elif isinstance(time_origin, str):
            self.time_origin_gps = Time(time_origin).gps
        else:
            self.time_origin_gps = Time(time_origin,format = 'mjd',scale = 'utc').gps


    def utc_to_met(self,utc,format=None,scale = None):

        if isinstance(utc,Time):
            gps = utc.gps
        else:
            try:
                gps = Time(utc,format = format,scale = scale).gps
            except (ValueError):
                gps = Time(utc,format = 'mjd',scale = scale).gps
        return gps - self.time_origin_gps
    def met_to_utc(self,met):

        gps = self.time_origin_gps + met

        return Time(gps,format = 'gps',scale = 'utc')


def findfile(dir1,feature):
    '''

    :param dir1:
    :param feature:
    :return:
    '''
    if (os.path.exists(dir1)):
        dirnames = os.listdir(dir1)
        filelist = []
        fil_number = 0
        fil_result_number = 0
        featurelist = [i for i in re.split('[*]',feature) if i != '']
        for_number = len(featurelist)
        fileresult = [[] for i in range(for_number)]
        for eve in range(for_number):
            if(eve == 0):
                fe_number = len(featurelist[eve])
                for sample in dirnames:
                    if (os.path.isfile(dir1 + sample)):
                        filelist.append(sample)
                        fil_number = fil_number + 1
                if (fil_number != 0):
                    for i in filelist:
                        i_number = len(i)
                        n = i_number - fe_number + 1
                        for j in range(n):
                            if (i[j:j + fe_number] == featurelist[eve]):
                                fileresult[eve].append(i)
                                fil_result_number = fil_result_number + 1
                                break
                    #print('1----------',fileresult[eve])#------------------------
                    if (fil_result_number == 0):
                        print('we do not find any file that has the feature with [' + feature + ']!\n')
                        return []
                    else:
                        fil_result_number = 0
                else:
                    print('there is no file in this dir ! \n')
                    return []
            else:
                fe_number = len(featurelist[eve])
                for i in fileresult[eve-1]:
                    i_number = len(i)
                    n = i_number - fe_number + 1
                    for j in range(n):
                        if (i[j:j + fe_number] == featurelist[eve]):
                            fileresult[eve].append(i)
                            fil_result_number = fil_result_number + 1
                            break
                if (fil_result_number == 0):
                    print('we do not find any file that has the feature with [' + feature + ']!\n')
                    return []
                else:
                    fil_result_number = 0
        return fileresult[for_number-1]
    else:
        print('do not find the dir named ['+ dir1 + ']!\n')
        return False


class Sky_map(object):

    def __init__(self,**kwargs):


        self.detector_color = '#74787c'
        self.detector_color_highlight = '#f26522'

        if 'figsize' in kwargs:
            self.size = kwargs['figsize'][0]
        else:
            self.size = None
        self.fig = plt.figure(**kwargs)
        self.ax = None



    def plot_earth(self, t, satellite, **kwargs):

        if 'facecolor' not in kwargs:
            kwargs['facecolor'] = '#90d7ec'
        if 'edgecolor' not in kwargs:
            kwargs['edgecolor'] = '#90d7ec'

        try:
            met, ra, dec, radius = satellite.get_earth_point(t)
            for i in range(len(met)):
                poly = SphericalPolygon.from_cone(ra[i],dec[i],radius[i],steps=180)
                x_,y_ = np.array(list(poly.to_radec())[0])
                earth = self.Polygon(list(zip(x_,y_))[::-1],**kwargs)
                self.ax.add_patch(earth)
        except (TypeError):
            met, ra, dec, radius = satellite.get_earth_point(t)
            poly = SphericalPolygon.from_cone(ra,dec,radius,steps=180)
            x_,y_ = np.array(list(poly.to_radec())[0])
            earth = self.Polygon(list(zip(x_,y_))[::-1],**kwargs)
            self.ax.add_patch(earth)


    def plot_detector(self, t,satellite,radius =10.0,good_detector_list = None,
              detector_color = None,detector_color_highlight = None,
              **kwargs):

        namelist = satellite.detectors.name
        try:
            len(t)
            print('only the first of t will be ploted')
            dete_point = satellite(t)
            for index,dete in enumerate(namelist):

                color = self.detector_color
                if detector_color is not None:
                    try:
                        color = detector_color[index]
                    except (TypeError):
                        color = detector_color

                if good_detector_list is not None:
                    if dete in good_detector_list:
                        color = self.detector_color_highlight
                        if detector_color_highlight is not None:
                            try:
                                color = detector_color_highlight[index]
                            except (TypeError):
                                color = detector_color_highlight
                ra,dec = dete_point[dete][0]
                poly = SphericalPolygon.from_cone(ra,dec,radius,steps=180)
                x_,y_ = np.array(list(poly.to_radec())[0])
                dete_p = self.Polygon(list(zip(x_,y_))[::-1],facecolor = color,edgecolor=color,linewidth=0.2*self.size,alpha=0.5,**kwargs)
                self.ax.add_patch(dete_p)
                self.text(ra,dec,str(dete),color = 'k',va = 'center',ha='center',size=self.size,**kwargs)
        except (TypeError):
            dete_point = satellite(t)
            for index,dete in enumerate(namelist):
                color = self.detector_color
                if detector_color is not None:
                    try:
                        color = detector_color[index]
                    except (TypeError):
                        color = detector_color
                if good_detector_list is not None:
                    if dete in good_detector_list:
                        color = self.detector_color_highlight
                        if detector_color_highlight is not None:
                            try:
                                color = detector_color_highlight[index]
                            except (TypeError):
                                color = detector_color_highlight
                ra,dec = dete_point[dete]
                poly = SphericalPolygon.from_cone(ra,dec,radius,steps=180)
                x_,y_ = np.array(list(poly.to_radec())[0])
                dete_p = self.Polygon(list(zip(x_,y_))[::-1],facecolor = color,edgecolor=color,linewidth=0.2*self.size,alpha=0.5,**kwargs)
                self.ax.add_patch(dete_p)
                self.text(ra,dec,str(dete),color = 'k',va = 'center',ha='center',size=self.size,**kwargs)


    def add_source(self, point, name=None):

        if isinstance(point,SkyCoord):
            ra = point.ra.deg
            dec = point.dec.deg
        else:
            ra = point[0]
            dec = point[1]
        self.plot(ra,dec,'*',color='r', markersize=self.size)
        if name is not None:
            try:
                for i in range(len(ra)):
                    self.text(ra[i],dec[i],name[i],va = 'bottom',ha='right',size=self.size)
            except(TypeError):
                self.text(ra,dec,str(name),va = 'bottom',ha='right',size=self.size)

    def plot_continue_source(self):
        ra = [299.591,224.980,135.529,83.633]
        dec = [35.2020, -15.639, -40.5547, 22.0069]
        name = ['CygX-1','SocX-1','VeleX-1','Crab']
        self.plot(ra,dec,'o',color='#c7a252', markersize=self.size)
        for ind_,name_i in enumerate(name):
            self.text(ra[ind_],dec[ind_],name_i,va = 'bottom',ha='right',size=self.size)


    def plot_galactic_plane(self):

        l = np.linspace(0,360,720)
        b = np.zeros(l.size)
        sky = SkyCoord(l=l,b=b,frame = 'galactic',unit = 'deg')
        self.plot(sky.icrs.ra.deg,sky.icrs.dec.deg,color = '#281f1d',linewidth=0.4*self.size,alpha=0.3)
        self.plot(sky.icrs.ra.deg,sky.icrs.dec.deg,color = '#281f1d',linewidth=0.2*self.size,alpha=0.5)
        self.plot(sky.icrs.ra.deg[0],sky.icrs.dec.deg[0],'o',markersize = 0.4*self.size,color = '#281f1d',alpha=0.5)
        self.plot(sky.icrs.ra.deg[0],sky.icrs.dec.deg[0],'o',markersize = 0.6*self.size,color = '#281f1d',alpha=0.3)
        return sky.icrs.ra.deg,sky.icrs.dec.deg

    def plot_sum(self,t,satellite):

        clock = satellite.clock
        utc_t = clock.met_to_utc(t)
        tmp_sun = get_sun(utc_t)
        self.plot(tmp_sun.ra.deg,tmp_sun.dec.deg,'o',color='#ffd400',markersize=2*self.size)
        self.text(tmp_sun.ra.deg,tmp_sun.dec.deg,'sun',size=self.size,va = 'center',ha='center')
        return tmp_sun

    def plot_moon(self, t,satellite):
        clock = satellite.clock
        time_utc = clock.met_to_utc(t)
        earth_r = get_body_barycentric('earth', time_utc)
        moon_r = get_body_barycentric('moon',time_utc )
        r_e_m = moon_r - earth_r
        e = satellite.get_pos(t)
        r = -e*satellite.pos_unit - np.array([r_e_m.x.value, r_e_m.y.value, r_e_m.z.value]) * u.km
        moon_point_d = cartesian_to_spherical(-r[0], -r[1], -r[2])
        self.plot(moon_point_d[2].deg, moon_point_d[1].deg, 'o', color='#72777b', markersize=1.5*self.size)
        self.text(moon_point_d[2].deg, moon_point_d[1].deg, 'moon', size=self.size,va = 'center',ha='center')

    def add_subplot(self, *args, **kwargs):
        if 'lon_0' in kwargs:
            lon_0 = kwargs['lon_0']
        else:
            lon_0 = 180
        if 'facecolor' not in kwargs:
            kwargs['facecolor'] = '#f6f5ec'
        self.ax = self.fig.add_subplot(projection=ccrs.Mollweide(central_longitude=lon_0), *args, **kwargs)
        self.set_coordinates(lon_0, size=self.size)
        return self.ax

    def legend(self,*args, **kwargs):
        return self.ax.legend(*args, **kwargs)

    def plot(self,*args, **kwargs):
        if self.ax is None:
            self.add_subplot(1,1,1)
        return self.ax.plot(transform=ccrs.Geodetic(),*args, **kwargs)

    def savefig(self,*args, **kwargs):
        return self.fig.savefig(*args, **kwargs)
    def close(self):
        plt.close(self.fig)
    def text(self,*args, **kwargs):
        if self.ax is None:
            self.add_subplot(1,1,1)
        return self.ax.text(transform=ccrs.Geodetic(),*args, **kwargs)
    def Polygon(self,*args, **kwargs):
        return Polygon(transform=ccrs.Geodetic(),*args, **kwargs)
    def add_patch(self,*args, **kwargs):
        return self.ax.add_patch(*args, **kwargs)

    def set_coordinates(self,lon_0,size = None):
        xticks = list(range(-180, 180, 30))
        yticks = list(range(-90, 90, 15))
        lons_x = np.arange(0,360,30)
        lons_y = np.zeros(lons_x.size)
        lats_y = np.arange(-75,76,15)
        lats_x = np.zeros(lats_y.size)
        self.ax.gridlines(xlocs=xticks, ylocs=yticks)
        lats_y_ticke = self.ax.projection.transform_points(ccrs.Geodetic(),lats_x+lon_0+179.99, lats_y*1.1)
        lats_y_x = lats_y_ticke[:,0]*0.86
        lats_y_y = lats_y_ticke[:,1]
        proj_xyz = self.ax.projection.transform_points(ccrs.Geodetic(),np.array([0,30]), np.array([0,0]))
        dx_ = np.abs(proj_xyz[0][0]-proj_xyz[1][0])
        for indexi,i in enumerate(lons_x):
            self.ax.text(i,lons_y[indexi],r'$%d^{\circ}$'%i,transform = ccrs.Geodetic(),size = size)
        for indexi,i in enumerate(lats_y):
            self.ax.text(lats_y_x[indexi]+dx_,lats_y_y[indexi],r'$%d^{\circ}$'%i,ha = 'right',va = 'center',size = size)
        self.ax.set_global()
        self.ax.invert_xaxis()

class Geometry(object):

    def __init__(self,pd_position_data,pos_unit = u.m,detectors = None, clock = None,name = 'a'):

        if detectors is not None:
            self.detectors = detectors
        else:
            self.detectors = Detectors(name=name)


        if clock is not None:

            self.clock = clock
        else:
            self.clock = Clock()


        met_time = pd_position_data['time'].values
        self.met_time_band = [met_time.min(), met_time.max()]
        met_time[0] = met_time[0] - 0.5
        met_time[-1] = met_time[-1] + 0.5


        qsj = pd_position_data[['q1', 'q2', 'q3', 'q4']].values
        self.deter_f = {}
        mat_list = self.get_transform_mat_more(qsj)
        for detec_i in self.detectors.get_names():
            vector = self.detectors(detec_i)
            position_list = []
            for mat in mat_list:
                X = np.mat(vector).T
                X1 = np.array(mat * X).T[0]
                position_list.append([X1[0],X1[1],X1[2]])
            position_list = np.array(position_list).T
            x_f = interp1d(met_time,position_list[0],kind = 'quadratic')
            y_f = interp1d(met_time, position_list[1], kind='quadratic')
            z_f = interp1d(met_time, position_list[2], kind='quadratic')
            self.deter_f[detec_i] = [x_f,y_f,z_f]
        self.pos_unit = pos_unit
        self.qsj0_f = interp1d(met_time,pd_position_data['q1'].values,kind='quadratic')
        self.qsj1_f = interp1d(met_time,pd_position_data['q2'].values,kind='quadratic')
        self.qsj2_f = interp1d(met_time,pd_position_data['q3'].values,kind='quadratic')
        self.qsj3_f = interp1d(met_time,pd_position_data['q4'].values,kind='quadratic')
        self.pos_x_f = interp1d(met_time,-pd_position_data['x'].values,kind='quadratic')
        self.pos_y_f = interp1d(met_time,-pd_position_data['y'].values,kind='quadratic')
        self.pos_z_f = interp1d(met_time,-pd_position_data['z'].values,kind='quadratic')

    def __call__(self, met_time):

        try:
            len(met_time)
            met_time = np.array(met_time)
            index_in = np.where((met_time >= self.met_time_band[0]) & (met_time <= self.met_time_band[-1]))[0]
            met_time_in = met_time[index_in]
            c = {'time': met_time_in}
            for detec in self.detectors.get_names():
                xf, yf, zf = self.deter_f[detec]
                x = xf(met_time_in)
                y = yf(met_time_in)
                z = zf(met_time_in)
                position = cartesian_to_spherical(x, y, z)
                c[detec] = np.vstack([position[2].deg, position[1].deg]).T
            return c

        except (TypeError):

            c = {'time': met_time}
            for detec in self.detectors.get_names():
                xf, yf, zf = self.deter_f[detec]
                x = xf(met_time)
                y = yf(met_time)
                z = zf(met_time)
                position = cartesian_to_spherical(x, y, z)
                c[detec] = [position[2].deg, position[1].deg]
            return c

    def get_good_detector(self,time,source):

        if isinstance(source,SkyCoord)==False:
            source = SkyCoord(ra=source[0],dec=source[1],frame = 'icrs',unit = 'deg')
        name = self.detectors.get_names()
        eff_ang = self.detectors.eff_angle
        return_list = []
        try:
            len(time)
            pd_sep = self.get_separation_with_time(time,source)
            col_name = pd_sep.columns[1:]
            data = pd_sep[col_name].values
            for i in data:
                d_ang = eff_ang-i
                index_ = np.where(d_ang>0)
                return_list.append(col_name[index_])
            return return_list
        except (TypeError):

            dete_centor = self(time)
            return_list = []
            for ni in name:
                center = dete_centor[ni]
                center = SkyCoord(ra = center[0],dec = center[1],frame = 'icrs',unit = 'deg')
                sep = center.separation(source).value
                if sep < self.detectors.get_eff_angle(ni):
                    return_list.append(ni)
            return return_list

    def get_separation_with_time(self,time,source):

        name = self.detectors.get_names()
        try:
            len(time)
            time = np.array(time)
            index_in = np.where((time >= self.met_time_band[0]) & (time <= self.met_time_band[-1]))[0]
            time_in = time[index_in]
            dete_centor = self(time_in)
            data = [time_in]
            col_name = ['time']
            for ni in name:
                center = (dete_centor[ni]).T
                center = SkyCoord(ra = center[0],dec = center[1],frame = 'icrs',unit = 'deg')
                data.append(center.separation(source).value)
                col_name.append(ni)
            data = np.vstack(data).T
        except(TypeError):
            data = [time]
            col_name = ['time']
            dete_centor = self(time)
            for ni in name:
                center = (dete_centor[ni])
                center = SkyCoord(ra = center[0],dec = center[1],frame = 'icrs',unit = 'deg')
                data.append(center.separation(source).value)
                col_name.append(ni)
            data = np.array(data)
        return 	pd.DataFrame(data=data,columns=col_name,dtype=np.float128)


    def get_earth_point(self,met_time):

        earth_radius = 6371. * u.km
        try:
            len(met_time)
            met_time = np.array(met_time)
            index_in = np.where((met_time >= self.met_time_band[0]) & (met_time <= self.met_time_band[-1]))[0]
            met_time_in = met_time[index_in]
            pos_x = self.pos_x_f(met_time_in)* self.pos_unit
            pos_y = self.pos_y_f(met_time_in)* self.pos_unit
            pos_z = self.pos_z_f(met_time_in)* self.pos_unit
            position = cartesian_to_spherical(pos_x,pos_y,pos_z)
            fermi_radius = np.sqrt(pos_x**2 + pos_y**2 + pos_z**2)
            radius_deg = np.rad2deg(np.arcsin((earth_radius / fermi_radius).to(u.dimensionless_unscaled)).value)
            return met_time_in,position[2].deg,position[1].deg,radius_deg

        except (TypeError):

            pos_x = self.pos_x_f(met_time)* self.pos_unit
            pos_y = self.pos_y_f(met_time)* self.pos_unit
            pos_z = self.pos_z_f(met_time)* self.pos_unit
            position = cartesian_to_spherical(pos_x,pos_y,pos_z)
            fermi_radius = np.sqrt(pos_x**2 + pos_y**2 + pos_z**2)
            radius_deg = np.rad2deg(np.arcsin((earth_radius / fermi_radius).to(u.dimensionless_unscaled)).value)
            return met_time,position[2].deg,position[1].deg,radius_deg


    def get_transform_mat_more(self,qsj):

        mat_list = []
        for qsj_i in qsj:
            mat_list.append(self.get_transform_mat_one(qsj_i))
        return mat_list

    def get_pos(self,time):

        try:
            len(time)
            pos_x = self.pos_x_f(time)
            pos_y = self.pos_y_f(time)
            pos_z = self.pos_z_f(time)
            pos = np.vstack([pos_x,pos_y,pos_z])
            return pos.T

        except (TypeError):

            return np.array([self.pos_x_f(time),self.pos_y_f(time),self.pos_z_f(time)])

    def get_qsj(self,time):

        try:
            len(time)
            qsj0 = self.qsj0_f(time)
            qsj1 = self.qsj1_f(time)
            qsj2 = self.qsj2_f(time)
            qsj3 = self.qsj3_f(time)
            qsj = np.vstack([qsj0,qsj1,qsj2,qsj3])
            return qsj.T

        except (TypeError):

            return np.array([self.qsj0_f(time),self.qsj1_f(time),self.qsj2_f(time),self.qsj3_f(time)])


    def get_transform_mat_one(self,qsj):

        p1,p2,p3,p0 = qsj
        mat = np.mat(np.zeros((3,3)))
        mat[0, 0] = p0 ** 2 + p1 ** 2 - p2 ** 2 - p3 ** 2
        mat[0, 1] = 2 * (p1 * p2 - p0 * p3)
        mat[0, 2] = 2 * (p0 * p2 + p1 * p3)
        mat[1, 0] = 2 * (p3 * p0 + p2 * p1)
        mat[1, 1] = p0 ** 2 + p2 ** 2 - p3 ** 2 - p1 ** 2
        mat[1, 2] = 2 * (p2 * p3 - p1 * p0)
        mat[2, 0] = 2 * (p1 * p3 - p0 * p2)
        mat[2, 1] = 2 * (p0 * p1 + p3 * p2)
        mat[2, 2] = p0 ** 2 + p3 ** 2 - p1 ** 2 - p2 ** 2
        return mat


    def transform_frame_one(self,vector3d,qsj):
        matr = self.get_transform_mat_one(qsj)
        X = np.mat(vector3d).T
        return np.array(matr * X).T[0]

    def inv_transform_frame_one(self,vector3d,qsj):
        matr = self.get_transform_mat_one(qsj)
        X = np.mat(vector3d).T
        return np.array(matr.I * X).T[0]


    def get_detector_centers(self,met_time):

        try:
            len(met_time)
            met_time = np.array(met_time)
            index_in = np.where((met_time>=self.met_time_band[0])&(met_time<=self.met_time_band[-1]))[0]
            met_time_in = met_time[index_in]
            qsj = self.get_qsj(met_time_in)

            c = {'time':met_time_in}

            for detec in self.detectors.get_names():
                c[detec] = []
                local_dete_ver = self.detectors(detec)
                for qsj_i in qsj:
                    dete_ver = self.transform_frame_one(local_dete_ver,qsj_i)
                    position = cartesian_to_spherical(dete_ver[0],dete_ver[1],dete_ver[2])
                    c[detec].append([position[2].deg,position[1].deg])
                c[detec] = np.array(c[detec])

            return c

        except (TypeError):

            qsj = self.get_qsj(met_time)
            c = {'time':met_time}
            for detec in self.detectors.get_names():
                local_dete_ver = self.detectors(detec)
                dete_ver = self.transform_frame_one(local_dete_ver,qsj)
                position = cartesian_to_spherical(dete_ver[0],dete_ver[1],dete_ver[2])
                c[detec] = [position[2].deg,position[1].deg]
            return c


class Daily_database(object):

    def __init__(self,topdir,clock = None):

        self.clock = clock
        self.topdir = topdir
        if self.clock is None:
            self.clock = Clock()

    def get_satellite_position(self,time_start,time_stop,format = None,scale='utc'):


        names = ['A','B']
        dir_list=['GECAM_A','GECAM_B']
        col_name= ['time','q1','q2','q3','q4','x','y','z','xw','yw','zw']

        if isinstance(time_start,Time) == False:
            time_start = Time(time_start, format=format, scale=scale)
        if isinstance(time_stop,Time) == False:
            time_stop =Time(time_stop,format=format,scale=scale)

        met_start = self.clock.utc_to_met(time_start)
        met_stop = self.clock.utc_to_met(time_stop)
        date_time_arr = pd.date_range(time_start.fits,time_stop.fits,freq = 'H')

        return_value = {}
        for i,dir_ in enumerate(dir_list):
            q1, q2, q3, q4 = [], [], [], []
            x, y, z = [], [], []
            xw, yw, zw = [], [], []
            time = []
            for t_i in range(date_time_arr.shape[0]):
                date_t = date_time_arr[t_i]
                year = '%d' % date_t.year
                month = '%.2d' % date_t.month
                day = '%.2d' % date_t.day
                hour = '%.2d' % date_t.hour
                link = self.topdir + year + '/' + month + '/' + day + '/'+dir_+'/'
                fm = '_posatt_' + year[-2:] + month + day + '_'+hour+ '_v'
                name_list= findfile(link,fm)
                if len(name_list)>0:
                    hl = fits.open(link+name_list[0])
                    data = hl[1].data
                    time_ = data.field(0)
                    q1_,q2_,q3_,q4_ = data.field(1),data.field(2),data.field(3),data.field(4)
                    x_,y_,z_ = data.field(9),data.field(10),data.field(11)
                    xw_,yw_,zw_ = data.field(15),data.field(16),data.field(17)
                    time.append(time_)
                    q1.append(q1_),q2.append(q2_),q3.append(q3_),q4.append(q4_)
                    x.append(x_),y.append(y_),z.append(z_)
                    xw.append(xw_),yw.append(yw_),zw.append(zw_)
                    hl.close()
                else:
                    print('warning! the file under line is lost!')
                    print(fm)
            if len(time)>0:
                time = np.concatenate(time)
                q1,q2,q3,q4 = np.concatenate(q1),np.concatenate(q2),np.concatenate(q3),np.concatenate(q4)
                x,y,z = np.concatenate(x),np.concatenate(y),np.concatenate(z)
                xw,yw,zw = np.concatenate(xw),np.concatenate(yw),np.concatenate(zw)
                inde_sort = np.argsort(time)
                new_data = np.vstack([time,q1,q2,q3,q4,x,y,z,xw,yw,zw]).T
                new_data = new_data[inde_sort]
                _,uni_index = np.unique(new_data[:,0],return_index=True)
                new_data = new_data[uni_index]
                index_ = np.where((new_data[:,0]>=met_start-2)&(new_data[:,0]<=met_stop+2))[0]
                new_data = new_data[index_]
                pd_data = pd.DataFrame(data=new_data,dtype=np.float128,columns=col_name)
                return_value[names[i]] = pd_data
            else:
                return_value[names[i]] = None

        return return_value

#-------------------------------------------------------------------------------
time_list_you_want = ['2020-12-09T21:15:00','2020-12-09T21:16:00',
                      '2020-12-09T21:17:00','2020-12-09T21:18:00']

source = SkyCoord(ra=293.729,dec= 21.3864,frame ='icrs',unit='deg')
name = 'SGRJ1935'

savedir = './results/'

daily_top = '/ws/FormalWork/GECAM_test/data/'                     #yours

#-------------------------------------------------------------------------------
daily = Daily_database(daily_top)                              #initialize daily database
GC_clock = Clock()                                             #initialize clock transform system

if os.path.exists(savedir)==False:
    os.makedirs(savedir)

met = GC_clock.utc_to_met(time_list_you_want)
utc_t = GC_clock.met_to_utc(met).fits
met_start = met.min()-1
met_stop = met.max()+1

daily_start = GC_clock.met_to_utc(met_start)
daily_stop = GC_clock.met_to_utc(met_stop)

position_data = daily.get_satellite_position(daily_start,daily_stop)

GC_A = Geometry(position_data['A'],pos_unit = u.m, name = 'a',clock=GC_clock)   #initialize GECAM geometry
GC_B = Geometry(position_data['B'],pos_unit = u.m, name = 'b',clock=GC_clock)   #initialize GECAM geometry

A_sep = GC_A.get_separation_with_time(met,source)
A_sep.to_csv(savedir+'A_GECAM_A_'+name+'_sep.csv',index=False)
B_sep = GC_B.get_separation_with_time(met,source)
B_sep.to_csv(savedir+'A_GECAM_B_'+name+'_sep.csv',index=False)

for i,t in enumerate(met):
    smp = Sky_map(figsize = (10,10))
    smp.add_subplot(2,1,1)
    smp.ax.set_title(utc_t[i])
    smp.plot_earth(t,GC_A)
    A_good_dete = GC_A.get_good_detector(t,source)
    smp.plot_continue_source()
    smp.plot_sum(t,GC_A)
    smp.add_source(source,name)
    smp.plot_moon(t,GC_A)
    smp.plot_detector(t,GC_A,good_detector_list=A_good_dete)
    smp.plot_galactic_plane()

    smp.add_subplot(2,1,2)
    smp.plot_continue_source()
    smp.add_source(source,name)
    B_good_dete = GC_B.get_good_detector(t,source)
    smp.plot_earth(t,GC_B)
    smp.plot_sum(t,GC_B)
    smp.plot_moon(t,GC_B)
    smp.plot_detector(t,GC_B,good_detector_list=B_good_dete)
    smp.plot_galactic_plane()
    smp.savefig(savedir + 'B_map_'+str(i)+'.png')
    smp.close()



