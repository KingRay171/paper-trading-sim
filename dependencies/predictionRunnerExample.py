#run this
import ml
import os
#from stock_prediction import GRU
#from stock_prediction import input_data
#from stock_prediction import ModelAccessor

print("starting up")
def run_model(ticker):
  path = rf"{os.getcwd()}/models/" +ticker+".sav"
  isExist = os.path.exists(path)
  
  print(path)
  print(isExist)
  model_9 = 0
  if(isExist):
    
    model_9 = ml.load_model(path)
    ml.run_main(ticker, model_9)
    

  else:
    #model = torch.load(path)
    ml.run_main(ticker)
    

  #print(model.runPredictions("ml_model/out.csv", 5, 30))
      
  
  

run_model('AMZN')
