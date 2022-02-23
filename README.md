# DiviPy - Streamlit

This is a small app, build with Streamlit. It will recommend up to 100 Stocks (with dividends) based on filters, and calculate some statics.
This is build, to help you find new stocks and then go and research them further. **This is NOT investment advice**, rather a help for finding new opportunities.</p> 

---
## How it works

<p>The application will take into account all of the filters and inputs, then look through round about 40k Stocks that pay out dividends. It will then calculate how long it takes to get to your goal, and how much money you need to invest in total, and in each stock. It will give you DataFrame Tables after 1-2-5Years and once you have reached your goal. You also have the option to exclude any Stock that it has spit out, in case you do not want that stock included.
This program calculates with a 100% reinvestment rate of the dividends you get. </p>


## Getting Started

If you want to host it on your local machine. [See Here](#executing-program)

If you want to use the online Streamlit Cloud hosted version, you currently have to wait a bit, as there is a critical error I'm trying to resolve with the Streamlit Devs that stops me from deploying.
You are however more than welcome to fork this repo and deploy it yourself.

## Dependencies

This program is using the included CSV ("Final_Stock_CSV"). It will not work without it, but you can substitute your own and re-write the functions to make sure that it can read the new csv data.

---

## Installing

If you want to run the program locally Install dependencies via 

``` pip install -r requirements.txt ```

## Executing program

Then once you have activated your virtual environment in the terminal
simply write

``` streamlit run interface.py ```

A new browser window should automatically open and you should be able to see the streamlit interface.

<p>
First locate the sidebar, and fill it out with your own filters, goals etc. The numbers are all before tax, so please keep that in mind.
</p>

<img src="https://i.imgur.com/wm6iavT.png">


<p>Press search and you will now see the middle area being populated by different DataFrames. The "you selected ..." will also be populated and an overview of the needed money / time and return will be displayed. It will then look like so. </p>


<img src="https://i.imgur.com/9l2Ivfy.png">

<p>Right underneath that you can see the different DataFrames in the different years. 1-2-5 Years and the one at the end when you have reached your goal. If you open them up you can see a rundown of all the stocks it recommended and how much you should be having (to reach your goal) at what point in time. </p>

<img src="https://i.imgur.com/Ty7hQS8.png">

<p>If you click the arrows in the top right, you can make the DataFrame fullscreen and get more information out of it. It will then look somewhat like this: </p>

<img src="https://i.imgur.com/nvvXBqX.png">

<p>Feel free to play around. I hope this app can help you make better and more informed financial decisions</p>

---

## Help

**This project is abandoned**, if you want to modify it for your own dataset or usage, feel free to do so.
If you want/need help, you can always reach out to me.

## Authors

Maximilian Sören Pollak

[Github](https://github.com/maximiliansoerenpollak)  
[LinkedIn](https://linkedin.com/in/msoerenpollak)

## Version History

* 0.2
    * Added Readme
    * Fixed interface.py to work with streamlit.
    * Added .gitignore
    * Added MIT License
* 0.1
    * Initial Commit

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details

