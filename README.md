Fashion Shopping Website with Personalized Recommendations and Integrated FAQ Chatbot
Overview
This project is a Fashion Shopping Website offering a personalized shopping experience by recommending clothing based on user-uploaded images. It uses image analysis to identify key features like hair type, face shape, and body shape to suggest clothing styles that suit the user.

Additionally, the website integrates a FAQ Chatbot that provides users with instant responses to common questions and a Razorpay payment gateway for secure transactions. Users can add items to their cart, choose Buy Now for immediate purchases, or select from payment options like Cash on Delivery and Netbanking.

Features
1. Personalized Fashion Recommendations
Users upload an image for analysis (hair, face, and body).
Based on the analysis, clothing and accessory recommendations are provided.
Users can buy recommended products directly or add them to the cart.
2. Add to Cart and Checkout System
Users can add items to their shopping cart for later purchase.
A cart summary with a total amount is displayed.
Items in the cart can be purchased at once during checkout.
3. Buy Now Option
Users can bypass the cart by selecting Buy Now to purchase individual items immediately.
This directs them to a checkout page for immediate payment.
4. FAQ Chatbot
The website includes an FAQ Chatbot that answers common questions like shipping policies, return policies, and payment methods.
The chatbot is preloaded with answers and allows users to quickly access information.
5. Razorpay Integration for Payments
Secure payment gateway integration using Razorpay.
Users can select payment methods like Netbanking or Cash on Delivery.
Handles payments securely with user-provided credentials after entering shipping and billing details.
6. Address and Payment Flow
Users are prompted to provide their shipping address and PIN code before proceeding to payment.
The system directs users to payment options, allowing them to complete their purchases.
7. Fully Responsive Design
The website has been designed using Tailwind CSS, ensuring that it is responsive and user-friendly across all devices.
Technologies Used
Frontend: HTML, CSS (Tailwind CSS), JavaScript
Backend: Python (Flask), MySQL for database management
Machine Learning: Image analysis using OpenCV
Payment Gateway: Razorpay integration
Chatbot: JavaScript-based FAQ Chatbot
Other Tools: Razorpay API, Flask-MySQLdb for database interaction

Getting Started
Prerequisites
Python 3.x
Flask Framework
MySQL Database
Node.js (if using advanced chatbot functionality)
Razorpay API Credentials (for payment gateway integration)



Features Overview:

Image Upload & Analysis
Users upload an image to receive personalized recommendations. The system uses OpenCV to analyze features like:

Hair Type: Long or short
Face Shape: Oval, round, square
Body Shape: Pear-shaped, inverted triangle, rectangular
Cart and Checkout System
Users can:

Add products to the cart
Proceed to checkout from the cart
Buy Now to immediately checkout a single product
Provide shipping address and choose payment options
Payment Gateway Integration
The system uses Razorpay for payment, offering:

Netbanking
Cash on Delivery
FAQ Chatbot
The chatbot answers user queries like:

"What is the return policy?"
"How can I track my order?"
"What payment methods are accepted?"
