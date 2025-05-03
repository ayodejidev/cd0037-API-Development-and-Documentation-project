import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../stylesheets/App.css';

const Header = () => {
  const location = useLocation();

  return (
    <div className='App-header'>
      <div className='header-content'>
        <Link to='/' className='nav-link'>
          <h1>Udacitrivia</h1>
        </Link>
        <nav className='nav-menu'>
          <Link 
            to='/' 
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            List
          </Link>
          <Link 
            to='/add' 
            className={`nav-link ${location.pathname === '/add' ? 'active' : ''}`}
          >
            Add
          </Link>
          <Link 
            to='/play' 
            className={`nav-link ${location.pathname === '/play' ? 'active' : ''}`}
          >
            Play
          </Link>
        </nav>
      </div>
    </div>
  );
};

export default Header;
