# oTree Gemini 

This is a simple chat app for [oTree](https://www.otree.org/) that is a recreation of the [oTree GPT app](https://github.com/clintmckenna/oTree_gpt) that I made. Instead of using Open AI's API, this uses Google Gemini.

## System Prompt 
As of this writing, Gemini does not allow a system prompt thought the API, but I use [this clever workaround](https://www.googlecloudcommunity.com/gc/AI-ML/Gemini-Pro-Context-Option/m-p/684704/highlight/true#M4159) in the code.

## API key
To use this, you will need to acquire a key from [Google's API](https://ai.google.dev/). Add this as an environment variable to your local environment to retrieve it.

## Package requirements
This uses Google's Generative AI Python package, which can be installed:
---
> <i>pip install google.generativeai</i>
---

## Model Parameters
Currently, I have this set up to use gemini-1.5-flash. You can adjust this model and the temperature in the \__init__.py file:

## Data Output
The text logs are saved in participant fields, but I also made a simple custom export function. This can be accessed in the "data" tab in oTree and will show the chat logs as a long-form csv.

## Citation
As part of oTree's [installation agreement](https://otree.readthedocs.io/en/master/install.html), be sure to cite their paper: 

- Chen, D.L., Schonger, M., Wickens, C., 2016. oTree - An open-source platform for laboratory, online and field experiments. Journal of Behavioral and Experimental Finance, vol 9: 88-97.

If this app was helpful, you may consider citing this github repository as well.

- McKenna, C., (2024). oTree Gemini. https://github.com/clintmckenna/oTree-Gemini