

with open('/content/drive/MyDrive/NDVI_UAV/Healthy/buffer_outer.csv', 'w', encoding='UTF8') as f:
  header = ['tre_id', 'h_minus','hist_0','hist_01', 'hist_02', 'hist_03','hist_04','hist_05','hist_06','hist_07','hist_08','hist_09']
  writer = csv.writer(f)
  writer.writerow(header)

  folder_path = '/content/drive/MyDrive/NDVI_UAV/Healthy/buffer_outer/'
  files = os.listdir(folder_path)
  print(files)
  for file in files :
    if file.endswith('.tif'):
      file_path = folder_path+file
      head, tail = os.path.split(file_path)
      tree_id = tail.split('.')[0]
      print("tree_id =========================== ",tree_id)

      src = rasterio.open(file_path)
      arr = src.read()
      arr = np.array(arr)
      arr.flatten()
      arr = arr[(arr > -3.4028235e+38)]
      #print(arr.shape)
      print("Raw Min = ",arr.min())
      print("Raw Max = ",arr.max())
      print("Raw Median = ",np.median(arr))

      arr = arr[(arr > arr.min())]
      print("removed nodata value")
      total_pixel = len(arr)
      print("total_pixels = ",total_pixel)

      ### Health index pixel counting
      # h0 <0 /h1 = 0-0.55 /h2 = 0.55-0.8 /h3 = >0.8
      h_minus = arr[(arr < 0)]
      h0 = arr[(arr >= 0) & (arr <= 0.1)]
      h1 = arr[(arr > 0.1) & (arr <= 0.2)]
      h2 = arr[(arr > 0.2) & (arr <= 0.3)]
      h3 = arr[(arr > 0.3) & (arr <= 0.4)]
      h4 = arr[(arr > 0.4) & (arr <= 0.5)]
      h5 = arr[(arr > 0.5) & (arr <= 0.6)]
      h6 = arr[(arr > 0.6) & (arr <= 0.7)]
      h7 = arr[(arr > 0.7) & (arr <= 0.8)]
      h8 = arr[(arr > 0.8) & (arr <= 0.9)]
      h9 = arr[(arr > 0.9)]

      #print("pixel count h_minus h0 h1 h2 h3 h4 h5 h6 h7 h8 h9 = ",len(h_minus),len(h0),len(h1),len(h2),len(h3),len(h4),len(h5),len(h6),len(h7),len(h8),len(h9))

      #### Health index calculate percentage
      h_minus_percent = round(((len(h_minus)/total_pixel)*100),2)
      h0_percent = round(((len(h0)/total_pixel)*100),2)
      h1_percent = round(((len(h1)/total_pixel)*100),2)
      h2_percent = round(((len(h2)/total_pixel)*100),2)
      h3_percent = round(((len(h3)/total_pixel)*100),2)
      h4_percent = round(((len(h4)/total_pixel)*100),2)
      h5_percent = round(((len(h5)/total_pixel)*100),2)
      h6_percent = round(((len(h6)/total_pixel)*100),2)
      h7_percent = round(((len(h7)/total_pixel)*100),2)
      h8_percent = round(((len(h8)/total_pixel)*100),2)
      h9_percent = round(((len(h9)/total_pixel)*100),2)
      print("**Percentage = ", h_minus_percent,h0_percent,h1_percent,h2_percent,h3_percent,h4_percent,h5_percent,h6_percent,h7_percent,h8_percent,h9_percent)

      data = [tree_id,h_minus_percent,h0_percent,h1_percent,h2_percent,h3_percent,h4_percent,h5_percent,h6_percent,h7_percent,h8_percent,h9_percent]

      # write the data
      writer.writerow(data)

      #tree_id,h0_percent,h1_percent,h2_percent,h3_percent#
      # ถ้า h1 มีมากกว่า 40 เปอร์เซนต์ คือป่วย
      # ถ้า h1 มีมากกว่า 50 เปอร์เซนต์ คือ ตาย/กาโน
