import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
// import App from './App';
// import registerServiceWorker from './registerServiceWorker';

// ReactDOM.render(<App />, document.getElementById('root'));
// registerServiceWorker();

import fetch from 'node-fetch';

function Square(props) {
  return (
    <button className="square" onClick={props.onClick}>
      {props.value}
    </button>
  );
}

class Board extends React.Component {
  renderSquare(i) {
    return (
      <Square
        value={this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
      />
    );
  }

  renderSquares(row_id, size) {
    const numbers = [];
    for(var i=0; i< size; i++)
    {
      numbers[i]=i;
    }
    const rows = numbers.map((i) =>
      <Square key={i.toString()}
            value={this.props.squares[size*row_id + i]}
            onClick={() => this.props.onClick(size*row_id + i)}
          />
    );
    return (
      <div className="board-row">
      {rows}    
      </div>);
  }

  renderBoard(size) {
    var numbers = [];
    for(var i=0; i< size; i++)
    {
      numbers[i]=i;
    }
    // const rows = numbers.map((i) =>
    //   <Square
    //         value={this.props.squares[i]}
    //         onClick={() => this.props.onClick(i)}
    //       />
    // );
    const board = numbers.map((i) =>
      <div key={i.toString()} className="board-row">
      {this.renderSquares(i, size)}  
    </div>
    );
    return (
      <div key="board" className="board">
      {board}    
      </div>);
  }

  render() {
    // return (
    //   <div>
    //       {this.renderSquares()}
    //     <div className="board-row">
    //       {this.renderSquare(3)}
    //       {this.renderSquare(4)}
    //       {this.renderSquare(5)}
    //     </div>
    //     <div className="board-row">
    //       {this.renderSquare(6)}
    //       {this.renderSquare(7)}
    //       {this.renderSquare(8)}
    //     </div>
    //   </div>
    // );
    return (this.renderBoard(11))
  }
}

class Game extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      history: [
        {
          squares: Array(9).fill(null)
        }
      ],
      stepNumber: 0,
      xIsNext: true
    };
  }

  handleClick(i) {
    const history = this.state.history.slice(0, this.state.stepNumber + 1);
    const current = history[history.length - 1];
    const squares = current.squares.slice();
    if (calculateWinner(squares) || squares[i]) {
      return;
    }
    squares[i] = this.state.xIsNext ? "X" : "O";
    this.setState({
      history: history.concat([
        {
          squares: squares
        }
      ]),
      stepNumber: history.length,
      xIsNext: !this.state.xIsNext
    });
    fetch('http://127.0.0.1:5000/')
    .then(res => res.text())
    .then(body => console.log(body));

    // fetch('http://127.0.0.1:5000/')
    // .then(res => res.json())
    // .then(json => console.log(json));
  }

  jumpTo(step) {
    this.setState({
      stepNumber: step,
      xIsNext: (step % 2) === 0
    });
  }

  render() {
    const history = this.state.history;
    const current = history[this.state.stepNumber];
    const winner = calculateWinner(current.squares);

    const moves = history.map((step, move) => {
      const desc = move ?
        'Go to move #' + move :
        'Go to game start';
      return (
        <li key={move}>
          <button onClick={() => this.jumpTo(move)}>{desc}</button>
        </li>
      );
    });

    let status;
    if (winner) {
      status = "Winner: " + winner;
    } else {
      status = "Next player: " + (this.state.xIsNext ? "X" : "O");
    }

    return (
      <div className="game">
        <div className="game-board">
          <Board
            squares={current.squares}
            onClick={i => this.handleClick(i)}
          />
        </div>
        <div className="game-info">
          <div>{status}</div>
          <ol>{moves}</ol>
        </div>
      </div>
    );
  }
}

// ========================================

ReactDOM.render(<Game />, document.getElementById("root"));

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}
