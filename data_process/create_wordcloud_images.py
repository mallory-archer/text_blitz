from matplotlib import pyplot as plt
import pickle
import os

# ----- DEFINE FUNCTIONS ----
def plot_wordcloud(wordcloud_object, plot_properties):
    for prop in plot_properties.keys():
        # wordcloud_object[prop] = plot_properties[prop]
        wordcloud_object.__setattr__(prop, plot_properties[prop])

    plt.figure(1, figsize=(12, 12))
    plt.axis('off')
    img_wordcloud = plt.imshow(wordcloud_object)
    # plt.show()
    return img_wordcloud

# ----- SET PARAMETERS -----
filepath_input_data = 'data_process/wordclouds'     #### DELETE DATA PROCESS WHEN RUNNING
filename_input_data = 'word_clouds.pkl'
filepath_output_data = 'data_process/wordclouds/word_cloud_images'         #### DELETE DATA PROCESS WHEN RUNNING
plot_properties = {'background_color': 'white', 'cmap': 'magma', 'max_font_size': 40, 'scale': 10, 'random_state': 1}

#####
select_phone = ['2165262546', '5635804952']     # + [None]
freq = ['all', 'year']      # 'month', 'day']
#####

# --- calculations
file_loc_input_data = os.path.join(filepath_input_data, filename_input_data)
with open(file_loc_input_data, "rb") as input_file:
    word_clouds = pickle.load(input_file)

for p in select_phone:
    for f in freq:
        for index, wordcloud_object in word_clouds[p][f].iteritems():
            if type(index) == str:
                temp = ''.join(str(x) for x in index)
            else:
                temp = '_'.join(str(x) for x in index)
            fn_temp = temp + '_img.png'
            file_loc_output_data = os.path.join(filepath_output_data, fn_temp)

            img_wordcloud = plot_wordcloud(wordcloud_object, plot_properties)

            plt.savefig(file_loc_output_data)