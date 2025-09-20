import google.generativeai as genai

# Configure the API key
genai.configure(api_key='AIzaSyBVhgsHDU53fM3dO-iHJcUgJQLLaG9BJnc')

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content based on a prompt
response = model.generate_content('What is the capital of India?')

# Print the generated response
print(response.text)
