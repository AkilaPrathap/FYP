import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const App = () => {
  const [messages, setMessages] = useState([
    { text: 'Hello! How can I help you today?', sender: 'bot' },
  ]);
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.post('http://localhost:5000/ask', { question: '' });
        const answer = response.data.answer;
        setMessages(prevMessages => [...prevMessages, { text: answer, sender: 'bot' }]);
      } catch (error) {
        console.error('Error fetching response from the server:', error);
        setMessages(prevMessages => [...prevMessages, { text: 'Oops! Something went wrong.', sender: 'bot' }]);
      }
    };

    fetchData();
  }, []); // Empty dependency array to run only once on component mount

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() !== '') {
      // Create a new message object for the user's input
      const newUserMessage = { text: inputValue, sender: 'user' };

      // Update the messages state to include the user's input
      setMessages(prevMessages => [...prevMessages, newUserMessage]);

      // Clear the input field after sending the message
      setInputValue('');

      try {
        // Make a POST request to the server with the user's question
        const response = await axios.post('http://localhost:5000/ask', {
          question: inputValue,
        });

        // Get the answer from the server response
        const answer = response.data.answer;

        // Create a new message object for the bot's answer
        const newBotMessage = { text: answer, sender: 'bot' };

        // Update the messages state to include the bot's answer
        setMessages(prevMessages => [...prevMessages, newBotMessage]);
      } catch (error) {
        console.error('Error fetching response from the server:', error);
        // Handle error (e.g., display an error message to the user)
        const errorMessage = { text: 'Oops! Something went wrong.', sender: 'bot' };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender === 'bot' ? 'bot-message' : 'user-message'}`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Type your message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default App;
