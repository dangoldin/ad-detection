import React from 'react';
import './App.css';
import axios from 'axios';

class Ad extends React.Component {
  render() {
    return (
      <li className="ad">
        <div className="twitter-account">
          {this.props.twitterAccount}
        </div>
        <div className="image">
          <img src={this.props.adUrl} />
        </div>
      </li>
    )
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      ads: []
    }
  }

  componentDidMount() {
    // const jsonAdsPath = 'http://localhost:8000/out.json'
    const jsonAdsPath = 'http://sleeping-giants.s3-website-us-east-1.amazonaws.com/out.json'
    axios.get(jsonAdsPath)
      .then(res => {
        const ads = res.data.ads
        this.setState({ ads });
      });
  }

  render() {
    const baseURL = 'http://sleeping-giants.s3-website-us-east-1.amazonaws.com/'
    const Ads = this.state.ads.map(function(ad, idx) {
      var adUrl = baseURL + ad.filename
      var twitterAccount = (ad.ad_info.twitter_account || '').split('/')[0];

      return (
        <Ad key={idx}
          twitterAccount={twitterAccount}
          adUrl={adUrl}
          />
      )
    })

    return (
      <div className="App">
        <div className="App-header">
          <h2>Welcome to Ad Detector</h2>
        </div>
        <div className="App-intro">
          <ul className="ads">
            {Ads}
          </ul>
        </div>
      </div>
    );
  }
}

export default App;
