# POST PROCESSING CONFIGURATION FILE FOR ISEE DASHBOARD

#------------------------------------------------------------------#
#                         TO CHANGE                                #
#------------------------------------------------------------------#

# string to add to the log file name
<<<<<<< feature/antoine
log_name='WL_ISEE_2D_PLAN_SECTION_TILE'

# PI Code for tiled PI : ['SAUV_2D', 'IERM_2D', 'CWRM_2D', 'IXEX_RPI_2D', 'CHNI_2D', 'ERIW_MIN_2D', 'PIKE_2D', 'WL_ISEE_2D']
pis_2D_tiled=['IXEX_RPI_2D', 'CHNI_2D', 'ERIW_MIN_2D', 'PIKE_2D'] # empty if no tiled PI

# PI Code for PI not tiled : ['WASTE_WATER_2D', 'AYL_2D', 'BIRDS_2D', 'MFI_2D', 'NFB_2D', 'ROADS_2D', 'WATER_INTAKES_2D']
pis_2D_not_tiled=['WASTE_WATER_2D', 'AYL_2D', 'BIRDS_2D', 'MFI_2D', 'NFB_2D', 'ROADS_2D', 'WATER_INTAKES_2D'] # empty if no PI not tiled
=======
log_name='WATER_INTAKES_2D_AB'

# PI Code for tiled PI : ['SAUV_2D', 'IERM_2D', 'CWRM_2D', 'IXEX_RPI_2D', 'CHNI_2D', 'ERIW_MIN_2D', 'PIKE_2D']
pis_2D_tiled=['CHNI_2D'] # empty if no tiled PI

# PI Code for PI not tiled : ['WASTE_WATER_2D', 'AYL_2D', 'BIRDS_2D', 'MFI_2D', 'NFB_2D', 'ROADS_2D', 'WATER_INTAKES_2D']
pis_2D_not_tiled=['WATER_INTAKES_2D'] # empty if no PI not tiled
>>>>>>> main

# PI Code for 1D PI : ['SHORE_PROT_STRUC_1D', 'ERIW_MIN_1D', 'ONZI_OCCUPANCY_1D', 'TURTLE_1D', 'WL_GLRRM_1D', 'WL_ISEE_1D', 'ZIPA_1D']
pis_1D=['SHORE_PROT_STRUC_1D', 'ERIW_MIN_1D', 'ONZI_OCCUPANCY_1D', 'TURTLE_1D', 'WL_GLRRM_1D', 'WL_ISEE_1D', 'ZIPA_1D'] # empty if no 1D PI

# Path to ISEE results (dashboard formatted)
#ISEE_RES=fr'T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW'
ISEE_RES=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW'
ISEE_RES_parquet=fr'\\131.235.232.206\prod2\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_PARQUET'
#ISEE_RES=fr'F:\GLAM_DASHBOARD\prod\DASHBOARDS_RESULTS_PARQUET'

# Path to save the post-processed ISEE results
POST_PROCESS_RES=fr'P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3'

ISEE_GRID_PATH=fr'\\131.235.232.206\prod2\GLAM\Input_ISEE\prod\GRID\grd_v44_20250527\feather'

temp_folder=r'F:\prod_temp'

# dossier pour creer bd de chaque plan (plus rapide quand cest en local)
duckbd_path=fr'F:\prod'


# Not implemented yet, you need to delete the files manually in POST_PROCESS_RES if you want to reprocess a plan/section
# However, it will be used to select which plans to upload to Azure, so you still need to set it
plans=['GERBL2_2014_ComboA', 'GERBL2_2014_ComboB','GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45','GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330']
# ['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD','OBS',
#        'PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45',
#        'PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330']

plans=['PreProjectHistorical', 'Bv7_2014', 'GERBL2_2014_ComboA', 'GERBL2_2014_ComboB', 'Bv7_2014_ComboC', 'GERBL2_2014_ComboD', 'OBS',
 'PreProject_RCP45', 'GERBL2_2014BOC_RCP45', 'GERBL2_2014_ComboA_RCP45', 'GERBL2_2014_ComboB_RCP45', 'GERBL2_2014_ComboC_RCP45', 'GERBL2_2014_ComboD_RCP45',
 'PreProject_STO_330', 'GERBL2_2014_STO_330', 'GERBL2_2014_ComboA_STO_330', 'GERBL2_2014_ComboB_STO_330', 'GERBL2_2014_ComboC_STO_330', 'GERBL2_2014_ComboD_STO_330']

# For a complete post-processing : ['PLAN','SECTION','TILE','PT_ID']
# You can keep all four for 1D PI and it won't cause an error it's going to skip them (TILE and PT_ID)
agg_type=['PLAN', 'SECTION', 'TILE'] #,'PT_ID']

#agg_type=['PLAN', 'SECTION', 'TILE', 'PT_ID']

#agg_type=['PT_ID']

#------------------------------------------------------------------#
#                           STABLE                                 #
#------------------------------------------------------------------#

name='ISEE'
# tiles_folder=r'P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_RAW_DATA\Tiles'
sep=';'

dct_tile_sect = {'LKO': [491, 490, 489, 488, 487, 486, 485, 484, 483, 482, 481, 480, 479, 478, 477, 476, 475, 474, 473, 472, 471, 470, 469, 468, 467, 466, 465, 464, 463, 462, 461, 460, 459, 458, 457, 456, 455, 454, 453, 452, 451, 450, 449, 448, 447, 446, 445, 444, 443, 442, 441, 440, 439, 438, 437, 436, 435, 434, 433, 432, 431, 430, 429, 428, 427, 426, 425, 424, 423, 422, 421, 420, 419, 418, 417, 416, 415, 414, 413, 412, 411, 410, 409, 408, 407, 406, 405, 404, 403, 402, 401, 400, 399, 398, 397, 396, 395, 394, 393, 392, 391, 390, 389, 388, 387, 386, 385, 384, 383, 382, 381, 380, 379, 378, 377, 376, 375, 374, 373, 372, 371, 370, 369, 368, 367, 366, 365, 364, 363, 362, 361, 360, 359, 358, 357, 356, 355, 354, 353, 352, 351, 350, 349, 348, 347, 346, 345, 344, 343, 342, 341, 340, 339, 338, 337, 336, 335, 334, 332, 331, 330, 329, 328, 327, 326, 325, 324, 323, 322, 321, 320, 319, 318, 317, 316, 315, 314, 313, 312, 311, 310, 309, 308, 307, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, 296, 295, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 226, 225, 224, 223, 222, 221, 220, 219, 216, 215, 214, 213, 212, 211, 210, 209, 208, 204, 203, 202, 201],
                 'SLR_DS': [121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84, 83, 82, 81, 79, 78, 74],
                'SLR_US': [166, 165, 164, 163, 162, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115],
                'USL_DS': [184, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 170, 169],
                'USL_US': [238, 237, 236, 228, 227, 226, 218, 217, 216, 207, 206, 205, 204, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180],
                 'LKO_CAN': [492, 491, 490, 489, 488, 487, 486, 485, 484, 483, 482, 481, 480, 479, 478, 477, 476, 475, 474, 473, 472, 471, 470, 469, 468, 467, 466, 465, 464, 463, 462, 461, 460, 459, 458, 457, 456, 455, 454, 453, 452, 451, 450, 449, 448, 447, 446, 445, 444, 443, 440, 439, 438, 437, 436, 435, 434, 433, 429, 428, 427, 426, 425, 421, 420, 419, 418, 417, 413, 412, 411, 410, 406, 405, 404, 403, 398, 397, 396, 395, 394, 390, 389, 388, 387, 386, 382, 381, 380, 379, 378, 374, 373, 372, 371, 370, 369, 365, 364, 363, 362, 361, 355, 354, 353, 352, 351, 350, 344, 343, 342, 341, 340, 339, 332, 331, 330, 329, 328, 327, 326, 325, 320, 319, 318, 317, 316, 315, 314, 313, 308, 307, 306, 305, 304, 303, 302, 301, 296, 295, 294, 293, 292, 291, 290, 289, 284, 283, 282, 281, 280, 279, 278, 277, 272, 271, 270, 269, 268, 267, 266, 261, 260, 259, 258, 257, 256, 255, 249, 248, 247, 246, 245, 238, 237, 236, 235, 228, 226],
'SLR_DS_CAN': [121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84, 83, 82, 81, 79, 78, 74],
'SLR_US_CAN': [166, 165, 164, 163, 162, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115],
'USL_DS_CAN': [182, 181, 179, 178, 176, 175, 173, 172, 170],
'USL_US_CAN': [238, 237, 236, 228, 227, 226, 218, 217, 216, 207, 206, 205, 200, 199, 198, 196, 195, 194, 192, 191, 190, 188, 187, 185, 184, 182, 181],
 'LKO_US': [462, 453, 452, 451, 450, 449, 444, 443, 442, 441, 440, 439, 438, 433, 432, 431, 430, 425, 424, 423, 422, 417, 416, 415, 414, 410, 409, 408, 407, 403, 402, 401, 400, 399, 394, 393, 392, 391, 386, 385, 384, 383, 378, 377, 376, 375, 369, 368, 367, 366, 361, 360, 359, 358, 357, 356, 350, 349, 348, 347, 346, 345, 339, 338, 337, 336, 335, 334, 325, 324, 323, 322, 321, 313, 312, 311, 310, 309, 301, 300, 299, 298, 297, 289, 288, 287, 286, 285, 277, 276, 275, 274, 273, 267, 266, 265, 264, 263, 262, 257, 256, 255, 254, 253, 252, 251, 250, 247, 246, 245, 244, 243, 242, 241, 240, 239, 236, 235, 234, 233, 232, 231, 230, 229, 226, 225, 224, 223, 222, 221, 220, 219, 216, 215, 214, 213, 212, 211, 210, 209, 208, 204, 203, 202, 201],
'USL_DS_US': [184, 182, 181, 180, 179, 178, 177, 176, 175, 174, 172, 170, 169],
'USL_US_US': [227, 226, 217, 216, 206, 205, 204, 199, 198, 197, 195, 194, 193, 191, 190, 189, 188, 187, 186, 185, 184, 183, 181, 180]
}

#------------------------------------------------------------------#
#                       OPTIONS TO COME                            #
#------------------------------------------------------------------#

# Not implemented yet
# overwrite=False # if True, existing files will be overwritten. if False, the plan and/or section will be skiped.

# Not implemented yet, you need to delete the files manually if you want to reprocess a plan/section
# sections=['LKO', 'USL_US', 'USL_DS', 'SLR_US', 'SLR_DS'] # sections may vary depending on the PI. Only the sections in this array AND available for the PI will be computed