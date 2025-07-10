import { useState, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthProvider';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { setIsLoggedIn } = useContext(AuthContext);

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    const userData = {
      username,
      password,
    };

    try {
      const response = await axios.post(
        'http://localhost:8000/api/v1/token/',
        userData
      );
      localStorage.setItem('accessToken', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      setIsLoggedIn(true);
      navigate('/');
    } catch (error) {
      console.error('Error during login:', error);
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 bg-light-dark p-5 rounded">
            <h3 className="text-light text-center mb-4">Login to our Portal</h3>
            <form onSubmit={handleLogin}>
              <div className="mb-3">
                <input
                  type="text"
                  className="form-control mb-3"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <input
                  type="password"
                  className="form-control"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && <div className="text-danger mb-3">{error}</div>}

              {loading ? (
                <button
                  disabled
                  type="submit"
                  className="btn btn-info d-block mx-auto w-100"
                >
                  <FontAwesomeIcon icon={faSpinner} spin />
                  &nbsp; Please wait...
                </button>
              ) : (
                <button
                  type="submit"
                  className="btn btn-info d-block mx-auto w-100"
                >
                  Login
                </button>
              )}
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default Login;
