// API communication module

/**
 * Verify content using the FastAPI backend
 */
async function verifyContent(content, inputType = 'text') {
    const apiEndpoint = await getApiEndpoint();
    const userId = await getUserId();
    const userEmail = await getUserEmail();

    const requestBody = {
        input_type: inputType,
        content: content,
        user_id: userId,
        user_email: userEmail
    };

    try {
        const response = await fetch(`${apiEndpoint}/api/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('API Error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Get user's verification history
 */
async function getHistory(limit = 50) {
    const apiEndpoint = await getApiEndpoint();
    const userId = await getUserId();

    try {
        const response = await fetch(`${apiEndpoint}/api/history/${userId}?limit=${limit}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('API Error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Get public feed
 */
async function getPublicFeed(limit = 20) {
    const apiEndpoint = await getApiEndpoint();

    try {
        const response = await fetch(`${apiEndpoint}/api/public-feed?limit=${limit}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('API Error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Test API connection
 */
async function testApiConnection() {
    const apiEndpoint = await getApiEndpoint();

    try {
        const response = await fetch(`${apiEndpoint}/test`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('API Connection Error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}
