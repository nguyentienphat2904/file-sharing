import { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { PeerModel } from '../models/peer.models';

export const register = async (req: Request, res: Response): Promise<void> => {
    const { username, password, address, port } = req.body;

    if (!username || !password || !address || !port) {
        res.status(400).json({ message: "Address, Port, Username and password are required" });
        return;
    }

    try {
        // Kiểm tra xem username đã tồn tại chưa
        const existingUser = await PeerModel.findOne({ username });
        if (existingUser) {
            res.status(400).json({ message: "Username already exists"});
            return;
        }

        // Hash mật khẩu
        const hashedPassword = await bcrypt.hash(password, 10);

        // Tạo người dùng mới
        const newUser = new PeerModel({
            username,
            password: hashedPassword,
            address: address,
            port: port,
        });

        await newUser.save();

        // Tạo JWT token
        const accessToken = jwt.sign(
            { id: newUser._id, username: newUser.username },
            process.env.JWT_ACCESS_SECRET as string
        );

        res.status(201).json({ message: "User registered successfully", accessToken });
    } catch (error) {
        console.error("Error in register:", error);
        res.status(500).json({ message: "Internal server error" });
    }
};

export const login = async (req: Request, res: Response) => {
    const { username, password } = req.body;

    if (!username || !password) {
        res.status(400).json({ message: "Username and password are required" });
        return;
    }

    try {
        const user = await PeerModel.findOne({ username });

        if (!user) {
            res.status(400).json({ message: "Invalid username or password" });
            return;
        }

        // Kiểm tra mật khẩu
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            res.status(400).json({ message: "Invalid username or password" });
            return;
        }

        const accessToken = jwt.sign(
            { id: user._id, username: user.username, role: user.role },
            process.env.JWT_ACCESS_SECRET as string,
        );
        res.json({ accessToken });
    } catch (error) {
        res.status(500).json({
            message: "Internal server error"
        })
    }
}