custom_telegram_js =\
"""
window.Telegram = {
    WebApp: {
        initData: "customData",
        initDataUnsafe: {
            query_id: "123456789",
            user: {
                id: 123456789,
                first_name: "John",
                last_name: "Doe",
                username: "johndoe",
                photo_url: "https://example.com/photo.jpg",
                auth_date: 1625247896,
                hash: "abc123hash"
            },
            chat: {
                id: 987654321,
                title: "Sample Chat",
                type: "private"
            },
        },
        getTransaction: function() {
            return {
                id: "transaction_id",
                amount: 100,
                currency: "USD"
            };
        },
        sendMessage: function(message) {
            console.log('Message sent:', message);
        },
        onEvent: function(event) {
            console.log('Event received:', event);
        },
        resize: function() {
            console.log('Window resized');
        },
        close: function() {
            console.log('App closed');
        },
    }
};
console.log('Custom Telegram object injected:', window.Telegram);
"""
