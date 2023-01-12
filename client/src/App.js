import React from 'react';
import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [prevAnswer, setPrevAnswer] = useState('');
  const [conversationId, setConversationId] = useState(''); 
  const inputRef = React.useRef();
  const handleSubmit = (e) => {
    e.preventDefault();
    setQuestions([...questions, e.target.elements.question.value]);
    inputRef.current.value = '';
  };



  useEffect(() => {
    const getAnswer = async () => {
      if (questions.length === 0) {
        return;
      }
      let response = await fetch(`http://127.0.0.1:5001/ask?q=${questions[0]}&conversation_id=${conversationId}`); 
      response = await response.json();
      setAnswers([...answers, response.answers]);
      setQuestions([]);  
      setPrevAnswer(prevAnswer + '\n你: ' + questions[0] + '\n\nChatBot:' + response.answers + '\n');
    
    };
    getAnswer();
  }, [questions]);
  useEffect(() => {
    const getNewConversationId = async () => {
      let response = await fetch(`http://127.0.0.1:5001/new-conversation`);
      response = await response.json();
      const id = response.id;
      setConversationId(id); 
    };
    getNewConversationId();
  }, []);
  useEffect(() => {
    document.querySelector('.answer-area').scrollTop = document.querySelector('.answer-area').scrollHeight;
  }, [prevAnswer]);

  return (
    <div className='container'>
      <pre className='answer-area'>
        {prevAnswer}
        <br />
      </pre>
      <form onSubmit={handleSubmit} className='question-form'>
        <input name='question' ref={inputRef} type='text' />
        <input type='submit' value='问' />
      </form>
    </div>
  );
}

export default App;
