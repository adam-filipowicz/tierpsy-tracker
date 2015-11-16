# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 01:56:06 2015

@author: ajaver
"""
import os

from getIndividualWormVideos import getIndividualWormVideos

import sys
import time
import h5py
import shutil
sys.path.append('../videoCompression/')

def createVideosWorker(masked_movies_dir, trajectories_dir, main_video_save_dir, base_name, status_queue= ''):
    masked_image_file = masked_movies_dir + base_name + '.hdf5'
    trajectories_file = trajectories_dir + base_name + '_trajectories.hdf5'
    segworm_file = trajectories_dir + base_name + '_segworm.hdf5'
    video_save_dir = main_video_save_dir + base_name + os.sep
    
    if os.path.exists(video_save_dir):
        shutil.rmtree(video_save_dir);
     
    #create movies of individual worms
    getIndividualWormVideos(masked_image_file, trajectories_file, \
    segworm_file, video_save_dir, is_draw_contour = True, max_frame_number = -1,\
    base_name = base_name, status_queue=status_queue)

    video_save_dir_gray = main_video_save_dir + base_name + '_gray' + os.sep
    getIndividualWormVideos(masked_image_file, trajectories_file, \
    segworm_file, video_save_dir_gray, is_draw_contour = False, max_frame_number = -1,\
    base_name = base_name, status_queue=status_queue)
    print base_name, 'Finished'

if __name__ == '__main__':
#python trackSingleFile.py "/Users/ajaver/Desktop/Gecko_compressed/20150323/" "/Users/ajaver/Desktop/Gecko_compressed/20150323/Trajectories/" "/Users/ajaver/Desktop/Gecko_compressed/20150323/Worm_Movies/" "Capture_Ch4_23032015_111907"
#    masked_movies_dir = '/Users/ajaver/Desktop/Gecko_compressed/20150323/'
#    trajectories_dir = '/Users/ajaver/Desktop/Gecko_compressed/20150323/Trajectories/'
#    main_video_save_dir = '/Users/ajaver/Desktop/Gecko_compressed/20150323/Worm_Movies/'
#    masked_movies_dir = '/Volumes/behavgenom$/Alex_Anderson/Compressed/Locomotion_videos_for_analysis_2015/';
#    trajectories_dir = '/Volumes/behavgenom$/Alex_Anderson/Trajectories/Locomotion_videos_for_analysis_2015/';
#    main_video_save_dir = '/Volumes/behavgenom$/Alex_Anderson/Worm_Movies/Locomotion_videos_for_analysis_2015/';
#    base_name = '149_3'
    masked_movies_dir = sys.argv[1]
    trajectories_dir = sys.argv[2]
    main_video_save_dir = sys.argv[3]
    base_name = sys.argv[4]
    
    #getTrajectoriesWorker(masked_movies_dir, trajectories_dir, base_name)
    createVideosWorker(masked_movies_dir, trajectories_dir, main_video_save_dir, base_name)
    
    