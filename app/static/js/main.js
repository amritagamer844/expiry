// Global utility functions and event handlers

// Format date to YYYY-MM-DD for input fields
function formatDateForInput(date) {
    const d = new Date(date);
    const month = ('0' + (d.getMonth() + 1)).slice(-2);
    const day = ('0' + d.getDate()).slice(-2);
    return d.getFullYear() + '-' + month + '-' + day;
}

// Calculate days between two dates
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    return Math.round(Math.abs((firstDate - secondDate) / oneDay));
}

// Check if a date is expired
function isExpired(date) {
    return new Date(date) < new Date();
}

// Update expiry status display
function updateExpiryStatus(dateString) {
    const expiryDate = new Date(dateString);
    const today = new Date();

    let statusHtml = '';
    if (isExpired(expiryDate)) {
        statusHtml = '<div class="alert alert-danger">This product is expired!</div>';
    } else {
        const daysRemaining = daysBetween(today, expiryDate);
        statusHtml = `<div class="alert alert-success">This product will expire in ${daysRemaining} days.</div>`;
    }

    $('#expiry-status').html(statusHtml);
}

// Document ready function
$(document).ready(function () {
    // Process expiry date image
    $('#process-expiry-btn').click(function () {
        const fileInput = document.getElementById('expiry_image');
        if (!fileInput || fileInput.files.length === 0) {
            alert('Please select an image first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        $.ajax({
            url: '/process_expiry_image',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    $('#expiry_date').val(response.date);

                    // Update expiry status
                    let statusHtml = '';
                    if (response.expired) {
                        statusHtml = '<div class="alert alert-danger">This product is expired!</div>';
                    } else {
                        statusHtml = `<div class="alert alert-success">This product will expire in ${response.days_remaining} days.</div>`;
                    }
                    $('#expiry-status').html(statusHtml);
                } else {
                    alert('Could not extract expiry date from the image. Please enter it manually.');
                }
            },
            error: function () {
                alert('Error processing the image. Please try again or enter the date manually.');
            }
        });
    });

    // Process barcode image
    $('#process-barcode-btn').click(function () {
        const fileInput = document.getElementById('barcode_image');
        if (!fileInput || fileInput.files.length === 0) {
            alert('Please select an image first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        $.ajax({
            url: '/process_barcode_image',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    $('#barcode').val(response.barcode);
                    if (response.product_name) {
                        $('#product_name').val(response.product_name);
                    }
                } else {
                    alert('Could not extract barcode from the image. Please enter it manually.');
                }
            },
            error: function () {
                alert('Error processing the image. Please try again or enter the barcode manually.');
            }
        });
    });

    // Show storage tips modal
    $('#storage-tips-btn').click(function () {
        const category = $('#category').val();
        if (!category) {
            alert('Please select a food category first.');
            return;
        }

        $.ajax({
            url: '/get_storage_tips/' + category,
            type: 'GET',
            success: function (response) {
                let tipsHtml = `<h4>${category}</h4><hr>`;

                for (const [location, tip] of Object.entries(response)) {
                    tipsHtml += `<h5>${location}</h5><p>${tip}</p>`;
                }

                $('#storage-tips-content').html(tipsHtml);
                $('#storageTipsModal').modal('show');
            },
            error: function () {
                alert('Error loading storage tips. Please try again.');
            }
        });
    });

    // Show nutrition information
    $('.nutrition-btn').click(function () {
        const itemId = $(this).data('id');

        $.ajax({
            url: '/get_nutrition/' + itemId,
            type: 'GET',
            success: function (response) {
                if (response.error) {
                    $('#nutrition-content').html(`<div class="alert alert-danger">${response.error}</div>`);
                } else {
                    let nutritionHtml = `
                        <div class="row">
                            <div class="col-md-4">
                                ${response.product_image ? `<img src="${response.product_image}" class="img-fluid mb-3" alt="${response.product_name}">` : ''}
                            </div>
                            <div class="col-md-8">
                                <h4>${response.product_name}</h4>
                                <p><strong>Barcode:</strong> ${response.barcode}</p>
                                
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Nutrient</th>
                                            <th>Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Energy</td>
                                            <td>${response.energy_kcal} kcal</td>
                                        </tr>
                                        <tr>
                                            <td>Fat</td>
                                            <td>${response.fat} g</td>
                                        </tr>
                                        <tr>
                                            <td>Carbohydrates</td>
                                            <td>${response.carbohydrates} g</td>
                                        </tr>
                                        <tr>
                                            <td>Proteins</td>
                                            <td>${response.proteins} g</td>
                                        </tr>
                                        <tr>
                                            <td>Salt</td>
                                            <td>${response.salt} g</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;

                    $('#nutrition-content').html(nutritionHtml);
                }

                $('#nutritionModal').modal('show');
            },
            error: function () {
                $('#nutrition-content').html('<div class="alert alert-danger">Error loading nutrition information. Please try again.</div>');
                $('#nutritionModal').modal('show');
            }
        });
    });

    // Show recipe suggestions
    $('.recipe-btn').click(function () {
        const itemId = $(this).data('id');

        $.ajax({
            url: '/get_item_recipes/' + itemId,
            type: 'GET',
            success: function (response) {
                if (response.error) {
                    $('#recipe-content').html(`<div class="alert alert-danger">${response.error}</div>`);
                } else if (response.length === 0) {
                    $('#recipe-content').html('<div class="alert alert-info">No recipes found for this item.</div>');
                } else {
                    let recipesHtml = '<div class="row">';

                    response.forEach(recipe => {
                        recipesHtml += `
                            <div class="col-md-6 mb-4">
                                <div class="card h-100">
                                    ${recipe.image ? `<img src="${recipe.image}" class="card-img-top" alt="${recipe.title}">` : ''}
                                    <div class="card-body">
                                        <h5 class="card-title">${recipe.title}</h5>
                                        <p class="card-text">
                                            <span class="badge bg-success">${recipe.usedIngredientCount} used ingredients</span>
                                            <span class="badge bg-warning text-dark">${recipe.missedIngredientCount} missing ingredients</span>
                                            <span class="badge bg-info">${recipe.likes} likes</span>
                                        </p>
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    recipesHtml += '</div>';
                    $('#recipe-content').html(recipesHtml);
                }

                $('#recipeModal').modal('show');
            },
            error: function () {
                $('#recipe-content').html('<div class="alert alert-danger">Error loading recipes. Please try again.</div>');
                $('#recipeModal').modal('show');
            }
        });
    });

    // Update expiry status when date is changed manually
    $('#expiry_date').change(function () {
        const dateValue = $(this).val();
        if (dateValue) {
            updateExpiryStatus(dateValue);
        } else {
            $('#expiry-status').html('');
        }
    });
});

