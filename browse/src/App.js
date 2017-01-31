import React from 'react';
import './App.css';
import axios from 'axios';

class App extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      ads: []
    }
  }

  componentDidMount() {
    const jsonAdsPath = 'http://localhost:8000/out.json'
    axios.get(jsonAdsPath)
      .then(res => {
        const ads = res.data
        this.setState({ ads });
      });
  }

  render() {
    const AdsHTML = this.state.ads.map(function(ad, idx) {
      var adUrl = 'http://localhost:8000/' + ad.orig.split('/').slice(-1)[0]

      return (
        <div key={idx}>
          <span>{ad.twitter_account}</span>
          <img src={adUrl} width="400px"></img>
        </div>
      )
    })

    return (
      <div className="App">
        <div className="App-header">
          <h2>Welcome to Ad Detector</h2>
        </div>
        <div className="App-intro">
          {AdsHTML}
        </div>
      </div>
    );
  }
}

export default App;
