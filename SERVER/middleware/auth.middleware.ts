import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

let refreshTokens: any[] = [];

const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const authorizationHeader = req.headers['authorization'];
    const token = authorizationHeader?.split(' ')[1];
    if (!token) {
        res.status(401).json({
            message: "Invalid token"
        })
    }
    jwt.verify(token as string, process.env.JWT_ACCESS_SECRET as string, (err, data) => {
        if (err) {
            res.sendStatus(403);
        }
        next();
    })
}

const login = async (req: Request, res: Response) => {
    const data = req.body;

    try {
        const acessToken = jwt.sign(data, process.env.JWT_ACCESS_SECRET as string, { expiresIn: '30s' });
        const refreshToken = jwt.sign(data, process.env.JWT_REFRESH_SECRET as string);
        refreshTokens.push(refreshToken);
        res.json({ acessToken, refreshToken });
    } catch (error) {
        res.status(500).json({
            message: "Internal server error"
        })
    }
}

const refreshToken = (req: Request, res: Response) => {
    const refreshToken = req.body.token;
    if (!refreshToken) res.sendStatus(401);
    if (!refreshTokens.includes(refreshToken)) res.sendStatus(403);
    jwt.verify(refreshToken as string, process.env.JWT_REFRESH_SECRET as string, (err, data) => {
        if (err) {
            res.sendStatus(403);
        }
        // const acessToken = jwt.sign({ username: data.username }, process.env.JWT_ACCESS_SECRET as string, { expiresIn: '30s' });
    })
}

export { authMiddleware, login, refreshToken }