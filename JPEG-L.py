 
"""
Created on Sun Nov 28 18:27:32 2021

@author: m.benammar
for academic purposes only 
"""

from matplotlib import pyplot 
import numpy as np 
from PIL import Image as im
import jpeg_functions as fc 
import huffman_functions as hj 
import sys
# Quantization matrix 
Q = 85; # quality  factor of JPEG in %

Q_matrix = fc.quantization_matrix(Q) # Quantization matrix 
  
# Open the image (obtain an RGB image)
image_origin = im.open("ISAE_Logo_SEIS_clr.PNG")  
image_origin_eval = np.array(image_origin)

# Transform into YCrBR 
image_ycbcr = image_origin.convert('YCbCr') 
image_ycbcr_eval= np.array(image_ycbcr)
 
#  Troncate the image (to make simulations faster)
image_trunc = image_ycbcr_eval[644:724,624:704] 

#pyplot.imshow(image_trunc) 

# Initializations
n_row = np.size(image_trunc,0) # Number of rows 
n_col = np.size(image_trunc,1)  # Number of columns
N_blocks =  (np.round(n_row/8 * n_col/8 )).astype(np.int32) # Number of (8x8) blocks 

image_plane_rec = np.zeros((n_row,n_col,3),dtype=np.uint8) 
image_DC = np.zeros((N_blocks.astype(np.int32),3), dtype = np.int32)
image_DC_rec = np.zeros((N_blocks.astype(np.int32),3), dtype = np.int32)
image_AC = np.zeros((63*N_blocks,3),dtype = np.int32 )
image_AC_rec = np.zeros((63*N_blocks,3),dtype = np.int32 )
bits_per_pixel=np.zeros( 3 )

opt_cr_DC_list = []
cr_DC_list=[]
opt_cr_AC_list = []
cr_AC_list=[]
nbits_DC_list = []
nbits_AC_list=[]
total_bits=0
avg_l_DC=[]
avg_l_AC=[]
ent_DC_list=[]
ent_AC_list=[]

def compute_nbits_symbol(input_array):
    r = np.max(input_array)-np.min(input_array)+1
    nbits = np.ceil(np.log2(r))
    return nbits


# ---------------------------------------------------------------
#                          Compression 
#  --------------------------------------------------------------

for i_plane in range(0,3): 
    
    # Select a plane  Y, Cb, or Cr 
    image_plane = image_trunc[:,:,i_plane]

    for i_row in range(0,n_row,8): 
        for j_col in range(0,n_col,8):
            
            #  Compute the block number
            block_number =( np.round(i_row/8*(n_row/8)+ j_col/8 )).astype(np.int32)
 
            # Select of block of 8 by 8 pixels
            image_plane_block = image_plane[i_row:i_row+8, j_col:j_col+8]     
            
            # DCT transform
            image_dct = fc.DCT(image_plane_block)
            
            # Quantization
            image_dct_quant = np.round(image_dct/Q_matrix ).astype(np.int32)
            
            # Zigzag reading  
            image_dct_quant_zgzg =  fc.zigzag(image_dct_quant)            
        
            # Separate DC and AC components    
            image_DC[block_number,i_plane] = image_dct_quant_zgzg[0]  
            image_AC[block_number*63 + 1:(block_number+1)*63,i_plane] = image_dct_quant_zgzg[1:63]
    
    # ---- DC components processing    
    # DPCM coding over DC components 
    image_DC_DPCM = image_DC[1:N_blocks,i_plane] - image_DC[0:N_blocks-1,i_plane]
    image_DC_0 = image_DC[0,i_plane] # first DC constant (not compressed)
    
    #  Map the resulting values in categoeries and amplitudes
    image_DC_DPCM_cat = fc.DC_category_vect(image_DC_DPCM) 
    image_DC_DPCM_amp = fc.DC_amplitude_vect(image_DC_DPCM) 
    list_image_cat_DC = np.ndarray.tolist(image_DC_DPCM_cat)  # create a list of DC components
    
    
    # --------------------------Students work on DC components --------------------------------- 

    [lettercount_DC, nb_chr_DC] = hj.dict_freq_numbers(list_image_cat_DC, list(range(min(list_image_cat_DC),max(list_image_cat_DC)+1)))
    huffman_tree_dc = hj.build_huffman_tree(lettercount_DC)
    coding_dict_DC = hj.generate_code(huffman_tree_dc)
    compressed_DC = hj.compress(list_image_cat_DC, coding_dict_DC)
    decoding_dict_DC = hj.build_decoding_dict(coding_dict_DC)
    decompressed_cat_DC = hj.decompress(compressed_DC, decoding_dict_DC)
    

    nbits_symbol_DC = compute_nbits_symbol(image_DC_DPCM_cat)
    nbits_DC_list.append(nbits_symbol_DC)
    entropy_DC_channel = hj.computeEntropy(lettercount_DC)
    opt_DC_cr = nbits_symbol_DC/(entropy_DC_channel)
    opt_cr_DC_list.append(opt_DC_cr)
    actual_cr_DC = len(image_DC_DPCM_cat)*nbits_symbol_DC/len(compressed_DC)
    avg_l_DC.append(len(compressed_DC)/len(image_DC_DPCM_cat))
    cr_DC_list.append(actual_cr_DC)
    ent_DC_list.append(entropy_DC_channel)
    


    # Decompress with Huffman 
    # decompressed_cat_DC should be the output of your Huffman decompressor 
    print("DC Checker")
    print(decompressed_cat_DC == list_image_cat_DC) 
    
   
    # ---------------------------------------------------------------------------------------------
    
    # ---- AC components processing    
    # RLE coding over AC components  
    AC_coeff = image_AC[:,i_plane] 
    [AC_coeff_rl, AC_coeff_amp] = fc.RLE(AC_coeff)
    list_image_rl_AC = np.ndarray.tolist(AC_coeff_rl)
    
    # --------------------------Students work on AC components ---------------------------------
    # Compress with Huffman 
    # Decompress with Huffman 
    # Rdecompressed_cat_AC should be the output of your Huffman decompressor 
    # Compress with Huffman 
    alphabet_cat_AC = set()
    for pair in list_image_rl_AC:
        alphabet_cat_AC.update(pair)

    alphabet_cat_AC = list(alphabet_cat_AC)

    [lettercount_AC, nb_chr_AC] = hj.dict_freq_numbers_2(list_image_rl_AC, alphabet_cat_AC)
    huffman_tree_ac = hj.build_huffman_tree(lettercount_AC)
    coding_dict_AC = hj.generate_code_2(huffman_tree_ac)
    compressed_AC = hj.compress_2(list_image_rl_AC, coding_dict_AC)
    decoding_dict_AC = hj.build_decoding_dict(coding_dict_AC)
    decompressed_cat_AC = hj.decompress(compressed_AC, decoding_dict_AC)

    print("AC Checker")
    list_image_rl_AC_tuples = [tuple(pair) for pair in list_image_rl_AC]
    print(decompressed_cat_AC == list_image_rl_AC_tuples)

    nbits_array = [item for pair in AC_coeff_rl for item in pair]
    nbits_symbol_AC = compute_nbits_symbol(AC_coeff_rl)
    nbits_AC_list.append(nbits_symbol_AC)
    entropy_AC_channel = hj.computeEntropy(lettercount_AC)
    opt_AC_cr = nbits_symbol_AC/(entropy_AC_channel)
    opt_cr_AC_list.append(opt_AC_cr)
    actual_cr_AC = len(AC_coeff_rl)*nbits_symbol_AC/len(compressed_AC)
    cr_AC_list.append(actual_cr_AC)
    avg_l_AC.append(len(compressed_AC)/len(AC_coeff_rl))
    ent_AC_list.append(entropy_AC_channel)

# --------------------------------Students work on the nb_bit/ pixel ---------------------

    long_str_dc = "".join(image_DC_DPCM_amp)
    long_str_ac = "".join(AC_coeff_amp.values())
    total_bits_per_channel = len(compressed_DC) + len(compressed_AC) + len(long_str_ac) + len(long_str_dc)
    total_bits += total_bits_per_channel




    
# ---------------------------------------------------------------
#                      Decompression 
#  --------------------------------------------------------------
    # ---- DC components processing  
    # Map the  categories and amplitudes DC components back into values  
    decompressed_cat_DC = np.array(decompressed_cat_DC) 
    image_DC_DPCM_rec = (fc.cat_ampl_to_DC_vect(decompressed_cat_DC,image_DC_DPCM_amp)) 
    
    # DPCM decoding of DC components 
    image_DC_rec[0,i_plane]=image_DC_0
    for i_block in range(1,N_blocks):
        image_DC_rec[i_block,i_plane]= image_DC_rec[i_block-1,i_plane] + image_DC_DPCM_rec[i_block-1]
        
    # ---- AC components processing      
    # Map AC components back into their original values  
    decompressed_cat_AC = np.array(decompressed_cat_AC)  
    image_AC_rec[:,i_plane] =  fc.RLE_inv(decompressed_cat_AC,AC_coeff_amp)

    for i_row in range(0,n_row,8): 
        for j_col in range(0,n_col,8):
            
            block_number = (np.round(i_row/8*(n_row/8)+ j_col/8 )).astype(np.int32)  

            # Combining AC and DC components 
            image_dct_quant_zgzg_rec = np.zeros(64, dtype= np.int32)
            image_dct_quant_zgzg_rec[1:63]= image_AC_rec[block_number*63 + 1:(block_number+1)*63,i_plane]
            image_dct_quant_zgzg_rec[0] = image_DC_rec[block_number,i_plane]
             
            # Inverse zigzag reading  
            image_dct_quant_rec = fc.zigzag_inv(image_dct_quant_zgzg_rec)
            
            # De-Quantization
            image_dct_rec = image_dct_quant_rec*Q_matrix 
            
            # Inverse DCT
            image_rec =  fc.DCT_inv(image_dct_rec) 
            image_plane_rec[i_row:i_row+8, j_col:j_col+8,i_plane ] = image_rec.astype(np.uint8)
            
total_pixel = n_row * n_col
bits_per_image_jpegl = total_bits/total_pixel
print("number of bits per pixel = ", bits_per_image_jpegl)
print("compression ration total image: ", 24/bits_per_image_jpegl )


width = 0.2
channel_list = ['Y', 'Cb', 'Cr']
x_coords = np.arange(len(channel_list))


fig, axs = pyplot.subplots(1,2, sharey=True)
opt_cr_DC_list=np.array(opt_cr_DC_list)
cr_DC_list = np.array(cr_DC_list)
opt_cr_AC_list = np.array(opt_cr_AC_list)
cr_AC_list = np.array(cr_AC_list)
avg_l_DC=np.array(avg_l_DC)
avg_l_AC = np.array(avg_l_AC)
ent_DC_list=np.array(ent_DC_list)
ent_AC_list = np.array(ent_AC_list)

axs[0].bar(x_coords-2*width/2, ent_AC_list, width=width, color='g', label='Lower bound')
axs[0].bar(x_coords, avg_l_AC, width=width, color='b', label='Average length')
axs[0].bar(x_coords+2*width/2, ent_AC_list+1, width=width, color='r', label='Upper bound')
axs[0].set_xticks(x_coords, channel_list)
axs[0].set_xlabel('YCbCr channels')
axs[0].set_ylabel('Average length [bits/pixel]')
axs[0].set_title('AC components')
axs[0].legend()

axs[0].grid()


axs[1].bar(x_coords-2*width/2, ent_DC_list, width=width, color='g', label='Lower bound')
axs[1].bar(x_coords, avg_l_DC, width=width, color='b', label='Average length')
axs[1].bar(x_coords+2*width/2, ent_DC_list+1, width=width, color='r', label='Upper bound')
axs[1].set_xticks(x_coords, channel_list)
axs[1].set_xlabel('YCbCr channels')
axs[1].set_ylabel('Average length [bits/pixel]')
axs[1].set_title('DC components')
axs[1].legend()
axs[1].grid()

pyplot.suptitle('Assessment of Huffman coding')
pyplot.tight_layout()
pyplot.show()


# Recovering the image from the array of YCbCr
image_ycbcr_rec = im.fromarray(image_plane_rec,'YCbCr')

# Convert back to RGB
image_rec =  image_ycbcr_rec.convert('RGB')



# Plot the image 
pyplot.figure()
pyplot.imshow(image_rec)
pyplot.show() 

 
 
