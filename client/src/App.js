import React from 'react';
import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [prevAnswer, setPrevAnswer] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    setQuestions([...questions, e.target.elements.question.value]);
  };

  useEffect(() => {
    const getAnswer = async () => {
      if (questions.length === 0) {
        return;
      }
      let response = await fetch(`http://127.0.0.1:5000/ask?q=${questions[0]}`);
      response = await response.json();
      setAnswers([...answers, response.answers]);
      setQuestions(questions.slice(1));
      setPrevAnswer((prev) => prev + '\n你: ' + questions[0] + '\n\nChatBot:' + response.answers + '\n');
    };
    getAnswer();
  }, [questions]);

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
        <input name='question' type='text' />
        <input type='submit' value='Ask' />
      </form>
    </div>
  );
}

export default App;
