import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UserPlus } from 'lucide-react';

interface RegisterFormProps {
  onLoginClick: () => void;
}

const RegisterForm = ({ onLoginClick }: RegisterFormProps) => {
  return (
    <div className="animate-slide-in-left">
      <Card className="bg-card-glass/80 backdrop-blur-sm border border-border/20 shadow-glass">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto p-3 rounded-full bg-primary/10">
            <UserPlus className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">Create an Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" type="text" placeholder="yourusername" required className="bg-card-glass/50 border-border/20" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="trader@example.com" required className="bg-card-glass/50 border-border/20" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" required className="bg-card-glass/50 border-border/20" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" type="tel" placeholder="+1234567890" required className="bg-card-glass/50 border-border/20" />
            </div>
            <Button type="submit" variant="hero" className="w-full">
              Register
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Already have an account?{" "}
            <Button variant="link" className="p-0 h-auto text-primary" onClick={onLoginClick}>
              Login
            </Button>
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegisterForm;
