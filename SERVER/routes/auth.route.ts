import express from 'express';
import { login, register } from '../controller/auth.controller';
const router = express.Router();

// Định nghĩa route cho đăng ký
router.post('/register', register);
router.post('/login', login);

export default router;
