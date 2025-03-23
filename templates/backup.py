
# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('gender_selection'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html', title="Login", action_url=url_for('login'), button_text="Login", signup=False, show_confirm=False, signup_url=url_for('signup'))


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        # Check if the username already exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists!')
        else:
            # Hash the password and insert into the database
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
            mysql.connection.commit()
            flash('Signup successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('login.html', title="Sign Up", action_url=url_for('signup'), button_text="Sign Up", signup=True, show_confirm=True, login_url=url_for('login'))


# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check if email exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user:
            # Create token and send password reset email
            token = s.dumps(email, salt='email-confirm')
            link = url_for('reset_password', token=token, _external=True)

            msg = Message('Password Reset Request', sender='noreply@domain.com', recipients=[email])
            msg.body = f"Click the link to reset your password: {link}"
            mail.send(msg)

            flash('An email with password reset instructions has been sent to your email.')
            return redirect(url_for('login'))
        else:
            flash('Email not found.')

    return render_template('forgot_password.html')


# Reset Password Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('The reset link is invalid or has expired.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('reset_password', token=token))

        # Update the user's password in the database
        hashed_password = generate_password_hash(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET password = %s WHERE email = %s', (hashed_password, email))
        mysql.connection.commit()

        flash('Your password has been reset successfully.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# Social Login (Google OAuth example)
@app.route('/auth/google')
def google_login():
    # Implement your Google OAuth authentication logic here.
    flash('Google login is not implemented yet.')
    return redirect(url_for('login'))


@app.route('/auth/facebook')
def facebook_login():
    # Implement your Facebook OAuth authentication logic here.
    flash('Facebook login is not implemented yet.')
    return redirect(url_for('login'))

# Gender selection route
@app.route('/gender', methods=['GET', 'POST'])
def gender_selection():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        gender = request.form.get('gender')
        session['gender'] = gender
        return redirect(url_for('home'))
    
    return render_template('gender_selection.html')

# Home route for image upload
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in to access the home page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image file uploaded.')
            return render_template('index.html')

        file = request.files['image']
        if file.filename == '':
            flash('No file selected.')
            return render_template('index.html')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            image = cv2.imread(filepath)
            if image is None:
                flash('Error loading image.')
                return render_template('index.html')

            hair_type = analyze_hair(image)
            face_shape = analyze_face(image)
            body_shape = analyze_body(image)

            session['hair_type'] = hair_type
            session['face_shape'] = face_shape
            session['body_shape'] = body_shape

            return render_template('index.html', hair_type=hair_type, face_shape=face_shape, body_shape=body_shape)

    return render_template('index.html')

@app.route('/recommendations')
def recommendations():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Please log in to access recommendations.')
        return redirect(url_for('login'))

    gender = session.get('gender')
    hair_type = session.get('hair_type')
    face_shape = session.get('face_shape')
    body_shape = session.get('body_shape')

    if not gender or not hair_type or not face_shape or not body_shape:
        flash('Please complete the analysis first.')
        return redirect(url_for('home'))

    # Get the sort option from query parameters
    sort_option = request.args.get('sort')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Basic query
    query = """
        SELECT id, name, price, image, size, material
        FROM recommended_clothes
        WHERE gender = %s AND hair_type = %s AND face_shape = %s AND body_shape = %s
    """
    
    # Modify query based on sorting
    if sort_option == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_option == 'price_desc':
        query += " ORDER BY price DESC"
    
    cursor.execute(query, (gender, hair_type, face_shape, body_shape))
    recommended_clothes = cursor.fetchall()
    cursor.close()

    return render_template('recommendations.html', clothes=recommended_clothes, sort=sort_option)


# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/product/<int:product_id>')
def product_page(product_id):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch product details
        query = "SELECT * FROM recommended_clothes WHERE id = %s"
        cur.execute(query, (product_id,))
        product = cur.fetchone()

        # Fetch related products (e.g., products with similar materials)
        cur.execute("SELECT * FROM recommended_clothes WHERE material = %s AND id != %s LIMIT 4", (product['material'], product_id))
        related_products = cur.fetchall()

        # Fetch reviews for the product
        cur.execute("SELECT r.rating, r.review_text, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = %s", (product_id,))
        reviews = cur.fetchall()
        cur.close()

        if product:
            return render_template('product_page.html', product=product, reviews=reviews, related_products=related_products)
        else:
            flash("Product not found.")
            return redirect(url_for('recommendations'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('recommendations'))

@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'logged_in' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO wishlist (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
        mysql.connection.commit()
        cur.close()
        flash('Added to your wishlist!')
    else:
        flash('Please log in to add items to your wishlist.')
    
    return redirect(url_for('product_page', product_id=product_id))

# Add to Cart route
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name, price, image FROM recommended_clothes WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if product:
        cart_item = {
            'id': product['id'],
            'name': product['name'],
            'price': float(product['price']),
            'image': product['image'],
            'quantity': 1  
        }

        # Initialize cart if it doesn't exist
        if 'cart' not in session:
            session['cart'] = []

        # Check if item is already in the cart, update quantity if it is
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += 1
                break
        else:
            session['cart'].append(cart_item)

        flash(f"{product['name']} has been added to your cart.")
    else:
        flash("Product not found.")

    return redirect(url_for('product_page', product_id=product_id))

@app.route('/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    action = request.form.get('action')  # 'increase' or 'decrease'
    
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == product_id:
                # Increase or decrease quantity
                if action == 'increase':
                    item['quantity'] += 1
                elif action == 'decrease' and item['quantity'] > 1:
                    item['quantity'] -= 1
                # Update subtotal for this item
                item['subtotal'] = item['price'] * item['quantity']
                break
    
    # Recalculate the total price
    total = sum(item['price'] * item['quantity'] for item in session['cart'])
    session['total'] = total

    # After updating quantity, redirect to the cart view
    return redirect(url_for('view_cart'))



@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    
    return redirect(url_for('view_cart'))


# Checkout route - handles both Buy Now and Cart Checkout
@app.route('/checkout')
def checkout_page():
    # If the user clicked "Buy Now"
    if 'checkout_item' in session:
        # Handle Buy Now: single product checkout
        items = [session['checkout_item']]
        total = session['checkout_item']['price'] * session['checkout_item']['quantity']
    # If the user is checking out from the cart
    elif 'cart' in session and session['cart']:
        # Handle Add to Cart: multiple items checkout
        items = session['cart']
        total = sum(item['price'] * item['quantity'] for item in items)  # Sum total for all cart items
    else:
        flash("Your cart is empty.")
        return redirect(url_for('view_cart'))

    # Render the checkout page with the items and total
    return render_template('checkout.html', items=items, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'shipping_address' in session:
        # Retrieve the email and other address details from the session
        email = session['shipping_address'].get('email')
        name = session['shipping_address'].get('name')
        address = session['shipping_address'].get('address')
        city = session['shipping_address'].get('city')
        pincode = session['shipping_address'].get('pincode')

        # Send order confirmation email
        if email:
            try:
                msg = Message('Order Confirmation',
                              sender='your-gmail@example.com',
                              recipients=[email])
                msg.body = f"Dear {name},\n\nYour order has been successfully placed.\n\nShipping to: {address}, {city}, {pincode}\n\nThank you for shopping with us!"
                mail.send(msg)
                flash('Confirmation email sent successfully!')
            except Exception as e:
                flash(f"Failed to send confirmation email: {str(e)}")

    flash('Your order has been placed successfully!')
    session.pop('cart', None)
    session.pop('checkout_item', None)

    return redirect(url_for('order_success'))

# VIEW CART
@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])

    total = sum(item['price'] * item['quantity'] for item in cart)

    return render_template('cart.html', cart=cart, total=total)


# Clear cart route
@app.route('/clear_cart')
def clear_cart():
    try:
        session.pop('cart', None)  # Remove 'cart' from session if it exists
        flash('Cart cleared successfully.')
    except KeyError:
        flash('No cart found to clear.')  # In case 'cart' key doesn't exist
    except Exception as e:
        flash(f"An error occurred: {str(e)}")  # Catch any other exceptions
    return redirect(url_for('view_cart'))

# Route to display the address form
@app.route('/address', methods=['GET'])
def address():
    if 'checkout_item' not in session and 'cart' not in session:
        flash("Please proceed to checkout first.")
        return redirect(url_for('view_cart'))

    return render_template('address.html')

# Address submission route
@app.route('/submit_address', methods=['POST'])
def submit_address():
    # Get the address and email details from the form
    name = request.form.get('name')
    address = request.form.get('address')
    city = request.form.get('city')
    pincode = request.form.get('pincode')
    phone = request.form.get('phone')
    email = request.form.get('email')  # Get user's Gmail

    # Save the shipping address and email in session
    session['shipping_address'] = {
        'name': name,
        'address': address,
        'city': city,
        'pincode': pincode,
        'phone': phone,
        'email': email
    }

    return redirect(url_for('payment'))

@app.route('/payment')
def payment():
    # Ensure that the address has been entered
    if 'shipping_address' not in session:
        flash('Please enter your shipping address first.')
        return redirect(url_for('address'))

    # Check if this is a "Buy Now" or "Cart Checkout" flow
    if 'checkout_item' in session:
        # Handle Buy Now: single product checkout
        cart = [session['checkout_item']]  # Single item as a list
        total = session['checkout_item']['price'] * session['checkout_item']['quantity']
    elif 'cart' in session and session['cart']:
        # Handle Cart Checkout: multiple items
        cart = session['cart']
        total = sum(item['price'] * item['quantity'] for item in cart)
    else:
        # If there's no checkout item or cart, redirect to cart
        flash("Your cart is empty.")
        return redirect(url_for('view_cart'))

    # Render the payment page with the cart and total information
    return render_template('payment.html', cart=cart, total=total)


@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name, price, image FROM recommended_clothes WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if product:
        # Store the product as a checkout item in the session for "Buy Now"
        session['checkout_item'] = {
            'id': product['id'],
            'name': product['name'],
            'price': float(product['price']),
            'image': product['image'],
            'quantity': 1  # Default quantity to 1 for "Buy Now"
        }
        return redirect(url_for('payment'))  # Redirect directly to the payment page
    else:
        flash("Product not found.")
        return redirect(url_for('product_page', product_id=product_id))


@app.route('/process_paypal', methods=['POST'])
def process_paypal():
    # Handle PayPal payment confirmation
    if 'cart' in session and 'shipping_address' in session:
        # Logic to store the order details in your database
        # Example: You can save the order and mark it as 'Paid via PayPal'
        order_details = {
            'payment_method': 'PayPal',
            'cart_items': session['cart'],
            'shipping_address': session['shipping_address']
        }
        
        # After successfully saving the order, clear the cart
        session.pop('cart', None)
        
        flash("Payment completed successfully via PayPal.")
        return redirect(url_for('order_success'))
    else:
        flash("There was an error with your order. Please try again.")
        return redirect(url_for('payment'))


@app.route('/process_cod', methods=['POST'])
def process_cod():
    if 'cart' in session and 'shipping_address' in session:
        # Save the order details
        # Example: Save to the database with COD payment method
        
        # Clear the cart after placing the order
        session.pop('cart', None)
        flash("Order placed successfully with Cash on Delivery.")
        return redirect(url_for('order_success'))
    else:
        flash("There was an error with your order. Please try again.")
        return redirect(url_for('payment'))

@app.route('/order_success')
def order_success():
    # Show the order success message
    return render_template('order_success.html')

@app.route('/create_razorpay_order', methods=['POST'])
def create_razorpay_order():
    data = request.get_json()
    amount = data['amount']  # Amount in paisa (e.g., Rs. 1000 = 100000 paisa)
    
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1  # Automatically capture the payment
    }
    
    razorpay_order = razorpay_client.order.create(order_data)
    return jsonify(razorpay_order)    

@app.route('/verify_razorpay_payment', methods=['POST'])
def verify_razorpay_payment():
    data = request.get_json()

    # Verify payment signature
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        return jsonify({'success': True})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'success': False})
